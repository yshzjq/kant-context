"""제공 도우미. 파일 저장, 실행 명령, 토큰 계산, 실제 API 연결을 처리합니다."""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"
MODEL = "gpt-5.6-luna"
FIELDS = ("담당자", "마감일", "승인조건")
NOW = "2026-11-04"
RESERVE = 384
MARGIN = 128


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def load_data():
    return read_json(DATA / "scenario.json")


def prefix():
    return (DATA / "policy.txt").read_text(encoding="utf-8").strip()


def count_tokens(messages):
    # 고정 인코딩으로 직렬화한 요청을 비교합니다. 서버 사용량의 정확한 예측은 아닙니다.
    import tiktoken
    text = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    return len(tiktoken.get_encoding("o200k_base").encode(text))


def fact_lines(text):
    for line in text.splitlines():
        name, separator, value = line.partition(":")
        if separator and name.strip() in FIELDS and value.strip():
            yield name.strip(), value.strip()


def validate_budget(*values):
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("한도, 출력 예약량, 여유는 0 이상의 정수여야 합니다.")


def validate_memory_input(user_id, action, name, value):
    if not isinstance(user_id, str) or not re.fullmatch(r"[a-z0-9_-]+", user_id):
        raise ValueError("사용자 ID 형식이 맞지 않습니다.")
    if action not in {"create", "read", "update", "delete"} or name not in {"style", "task"}:
        raise ValueError("허용되지 않은 메모리 작업입니다.")
    if action in {"create", "update"}:
        if not isinstance(value, dict) or set(value) != {"text", "expires_at"}:
            raise ValueError("text, expires_at 두 필드를 사용하세요.")
        if not isinstance(value["text"], str) or not value["text"].strip():
            raise ValueError("기억 내용은 빈 문자열일 수 없습니다.")
        if not isinstance(value["expires_at"], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value["expires_at"]):
            raise ValueError("만료일은 YYYY-MM-DD 형식입니다.")
        from datetime import date
        date.fromisoformat(value["expires_at"])


def memory_demo(module, directory):
    path = Path(directory) / "memory.json"

    def input_messages(records):
        items = []
        for key in records:
            owner, name = key.split(":", 1)
            value = module.memory_action(records, owner, "read", name)
            if value is not None:
                items.append({"id": key, "kind": "memory", "user_id": owner,
                              "body": value["text"], "expires_at": value["expires_at"],
                              "trusted": True, "active": True, "priority": 1})
        context = module.select_context(items, "minji", NOW)
        return module.build_messages(prefix(), "내 설명 방식을 확인해 주세요.", context, [], {})

    records = {}
    module.memory_action(records, "minji", "create", "style",
                         {"text": "짧은 한국어 설명", "expires_at": "2026-12-04"})
    module.memory_action(records, "jihoon", "create", "style",
                         {"text": "자세한 한국어 설명", "expires_at": "2026-12-04"})
    session = {}
    module.memory_action(session, "minji", "create", "task",
                         {"text": "배포 승인 확인", "expires_at": NOW})
    session_before = module.memory_action(session, "minji", "read", "task")
    module.memory_action(session, "minji", "update", "task",
                         {"text": "보안팀 검토 결과 확인", "expires_at": NOW})
    session_after = module.memory_action(session, "minji", "read", "task")
    write_json(path, records)
    reopened = read_json(path)
    before = module.memory_action(reopened, "minji", "read", "style")
    messages_before = input_messages(reopened)
    module.memory_action(reopened, "minji", "update", "style",
                         {"text": "단계별 한국어 설명", "expires_at": "2026-12-04"})
    write_json(path, reopened)
    reopened = read_json(path)
    after = module.memory_action(reopened, "minji", "read", "style")
    messages_after = input_messages(reopened)
    module.memory_action(reopened, "minji", "delete", "style")
    write_json(path, reopened)
    reopened = read_json(path)
    messages_deleted = input_messages(reopened)
    module.memory_action(session, "minji", "delete", "task")
    return {"before": before, "after": after, "remaining": reopened,
            "messages_before": messages_before, "messages_after": messages_after,
            "messages_deleted": messages_deleted,
            "session_before": session_before, "session_after": session_after,
            "session_after_end": session,
            "scope": "이 실행에서 만든 memory.json의 활성 항목만 삭제합니다."}


def fixture_answer(messages):
    """사용자 메시지의 사실을 읽는 고정 함수입니다. 생성 모델이 아닙니다."""
    facts = {}
    for message in messages:
        if message["role"] != "user":
            continue
        content = message["content"]
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {}
        if isinstance(data, dict):
            for name, row in data.get("summary", {}).items():
                facts[name] = row["value"]
        for name, value in fact_lines(content):
            facts[name] = value
    return {name: facts.get(name, "확인 필요") for name in FIELDS}


def answer_score(answer, expected):
    return sum(answer.get(name) == expected[name] for name in FIELDS)


def usage_record(usage):
    details = usage.get("input_tokens_details") or {}
    fields = [usage.get("input_tokens"), usage.get("output_tokens"),
              details.get("cached_tokens"), details.get("cache_write_tokens")]
    if any(type(n) is not int or n < 0 for n in fields):
        return {"usage": usage, "estimated_cost_usd": None, "cache_observation": "계량 누락"}
    incoming, outgoing, cached, written = fields
    if cached + written > incoming:
        raise ValueError("캐시 계량이 입력 토큰보다 큽니다.")
    rates = read_json(DATA / "prices.json")
    cost = ((incoming - cached - written) * rates["input"] + cached * rates["cached"]
            + written * rates["cache_write"] + outgoing * rates["output"]) / 1_000_000
    return {"usage": usage, "estimated_cost_usd": round(cost, 10),
            "cache_observation": "읽기 관측" if cached else "읽기 0",
            "uncached_input_cost_usd": incoming * rates["input"] / 1_000_000,
            "actual_input_cost_usd": round(cost - outgoing * rates["output"] / 1_000_000, 10)}


def live_answer(messages, key, use_cache):
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv(ROOT / ".env", override=False)
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise ValueError(".env에 OPENAI_API_KEY를 설정하세요.")
    request_messages = copy.deepcopy(messages)
    if use_cache:
        first = request_messages[0]
        first["content"] = [{"type": "input_text", "text": first["content"],
                             "prompt_cache_breakpoint": {"mode": "explicit"}}]
    started = time.perf_counter()
    with OpenAI(max_retries=0, timeout=60) as client:
        response = client.responses.create(
            model=MODEL, input=request_messages, max_output_tokens=RESERVE,
            reasoning={"effort": "none"}, store=False,
            prompt_cache_key=key, prompt_cache_options={"mode": "explicit", "ttl": "30m"},
        )
    raw = response.model_dump(mode="json")
    if raw.get("status") != "completed":
        raise ValueError("모델 응답이 완료되지 않았습니다. 사용량과 오류를 확인하세요.")
    answer = json.loads(response.output_text)
    if not isinstance(answer, dict) or set(answer) != set(FIELDS) or any(not isinstance(v, str) for v in answer.values()):
        raise ValueError("모델이 세 문자열 필드의 JSON 형식으로 답하지 않았습니다.")
    return answer, {**usage_record(raw.get("usage") or {}),
                    "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                    "response_id": response.id, "model": raw.get("model")}


def compare(module, live=False):
    data = load_data()
    context = module.select_context(data["context"], data["user_id"], NOW)
    summary = module.summarize(data["turns"])
    records = []
    for name, limit, summary_value in (("전체 대화", 5000, {}),
                                        ("최근 대화", 2300, {}),
                                        ("요약과 최근 대화", 2300, summary)):
        make = lambda turns: module.build_messages(prefix(), data["question"], context, turns, summary_value)
        kept = module.select_window(data["turns"], limit, RESERVE, MARGIN, make, count_tokens)
        messages = make(kept)
        if live:
            answer, usage = live_answer(messages, module.cache_key(prefix(), data["user_id"]), False)
        else:
            answer, usage = fixture_answer(messages), {"usage": None, "estimated_cost_usd": None}
        records.append({"condition": name, "limit": limit, "input_budget": limit - RESERVE - MARGIN,
                        "estimated_input_tokens": count_tokens(messages),
                        "turn_ids": [turn["id"] for turn in kept], "answer": answer,
                        "exact_fields": answer_score(answer, data["expected"]), **usage})
    return {"mode": "live" if live else "fixture", "records": records,
            "note": "완전 일치 3항목은 작은 확인 지표입니다. 실제 답변은 원문과 직접 비교하세요."}


def cache_demo(module, live=False):
    data = load_data()
    context = module.select_context(data["context"], data["user_id"], NOW)
    summary = module.summarize(data["turns"])
    messages = module.build_messages(prefix(), data["question"], context, [], summary)
    key = module.cache_key(prefix(), data["user_id"])
    records = []
    if live:
        for enabled in (False, True, True):
            answer, usage = live_answer(messages, key, enabled)
            records.append({"cache_enabled": enabled, "answer": answer, **usage})
    return {"mode": "live" if live else "fixture", "prefix_tokens": count_tokens(messages[:1]),
            "cache_key": key, "records": records,
            "note": "fixture는 요청 구성을 확인합니다. 캐시 사용량과 비용은 --live에서만 관측합니다."}


def cli(module):
    parser = argparse.ArgumentParser(description="KANT NEXT DevDesk 입력과 기억 관리")
    parser.add_argument("command", choices=["demo", "run", "check", "challenge"])
    parser.add_argument("stage", nargs="?", choices=["context", "memory", "compare", "cache", "all", "challenge"])
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if args.live and (args.command != "run" or args.stage not in {"compare", "cache"}):
        parser.error("--live는 run compare 또는 run cache에서만 사용합니다.")
    try:
        if args.command == "demo":
            data = load_data()
            print(f"준비 완료: 자료 {len(data['context'])}개, 대화 {len(data['turns'])}턴. 아직 작성한 코드를 검사하지 않았습니다.")
            return 0
        if args.command == "check":
            import checks
            return checks.run(module, args.stage or "all")
        if args.command == "challenge" or args.stage == "challenge":
            data = load_data()
            result = module.merge_summary({"current": {}, "changes": [], "processed_ids": []}, data["turns"])
            stage = "challenge"
        elif args.stage == "memory":
            result = memory_demo(module, ARTIFACTS)
            stage = "memory"
        elif args.stage == "context":
            data = load_data()
            context = module.select_context(data["context"], data["user_id"], NOW)
            result = {"selected_ids": [row["id"] for row in context],
                      "messages": module.build_messages(prefix(), data["question"], context, [], {})}
            stage = "context"
        elif args.stage in {"compare", "cache"}:
            stage = args.stage
            result = compare(module, args.live) if stage == "compare" else cache_demo(module, args.live)
        else:
            parser.error("run 뒤에 context, memory, compare, cache 중 하나를 쓰세요.")
        path = ARTIFACTS / f"{stage}-{'live' if args.live else 'fixture'}.json"
        write_json(path, result)
        if stage == "context":
            print("선택 자료: " + ", ".join(result["selected_ids"]))
            print("메시지 역할: " + " -> ".join(row["role"] for row in result["messages"]))
        elif stage == "memory":
            print(f"기억 변경: {result['before']['text']} -> {result['after']['text']} -> 삭제")
            print("남은 기억: " + ", ".join(result["remaining"]))
            print("수정과 삭제 전후의 전체 입력은 결과 파일에서 확인하세요.")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"저장: {path}")
        return 0
    except NotImplementedError as error:
        print(f"미완료: {error}")
        return 1
    except (ValueError, KeyError) as error:
        print(f"실행 실패: {error}")
        return 1
    except Exception as error:
        status = getattr(error, "status_code", None)
        print(f"실행 실패: {type(error).__name__}" + (f" (HTTP {status})" if status else "") + ". 입력과 환경을 확인하세요.")
        return 1
