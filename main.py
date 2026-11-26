"""main.py의 todo(...) 부분을 작성하세요. support.py와 checks.py는 그대로 사용합니다."""
import copy
import hashlib
import json
import sys

import support


def todo(message):
    raise NotImplementedError(message)


# 필수 1. 필요한 자료와 사용자 기억 관리하기
def select_context(items, user_id, now):
    kept = []
    for item in items:
        # allowed = todo("접근 범위, 신뢰, 현행 여부와 만료 조건")
        allowed = (item["user_id"] == "public" or item["user_id"] == user_id) and item["trusted"] == True and item["active"] == True and (item["expires_at"] is None or item["expires_at"] > now)

        if allowed:
            kept.append(copy.deepcopy(item))
    # 이유: 높은 우선순위의 자료를 먼저 고르면 어떤 문제가 생기는지 적으세요.
    # 쓰면 안 되는 자료인지 먼저 걸러내고 우선도 높은 순으로 골라야 한다 그러지 않으면 다른 사용자의 자료나 만료된 자료들을 사용하게 된다
    return sorted(kept, key=lambda item: (-item["priority"], item["id"]))


def memory_action(records, user_id, action, name, value=None):
    support.validate_memory_input(user_id, action, name, value)
    key = f"{user_id}:{name}"
    if action == "read":
        #return todo("현재 사용자의 기억 조회")
        return copy.deepcopy(records.get(key))
    if action == "create":
        if key in records:
            raise ValueError("이미 있는 기억입니다. update를 사용하세요.")
        #records[key] = todo("새 기억 저장")
        records[key] = copy.deepcopy(value)
    elif action == "update":
        if key not in records:
            raise KeyError("수정할 기억이 없습니다.")
        #records[key] = todo("기존 기억 수정")
        records[key] = copy.deepcopy(value)
    elif action == "delete":
        #return todo("현재 사용자의 기억 삭제")
        return records.pop(key, None)
    return copy.deepcopy(records[key])


def build_messages(prefix, question, context, turns, summary):
    data = json.dumps({"reference_data": context, "summary": summary}, ensure_ascii=False)
    history = [message for turn in turns for message in turn["messages"]]
    # 이유: 장기기억과 세션 상태를 모두 저장하면 컨텍스트가 무거워지고, 지난 세션의 작업 메모가 남아 있으면 이미 끝난 일을 지금 일로 착각할 수 있다.
#       자료와 지시를 나누면 자료 속 문장이 지시로 취급되지 않고 참고 자료로만 쓰인다.
    # return todo("고정 지시, 참고 자료, 대화, 현재 질문 순서의 메시지")
    return [
        {"role": "developer", "content": prefix},   # 지시 
        {"role": "user", "content": data},            # 참고 자료
        *history,                                          # 지난 대화 (펼치기)
        {"role": "user", "content": question},            # 현재 질문
        ]


# 필수 2. 긴 대화를 줄이고 반복 입력 재사용하기
def summarize(turns):
    summary = {}
    for turn in turns:
        for name, value in support.fact_lines(turn["messages"][0]["content"]):
            #summary[name] = todo("최신 값과 출처 턴")
            summary[name] = {"value" : value, "source_turn_id" : turn["id"]}
    return summary


def select_window(turns, limit, reserve, margin, make_messages, count):
    support.validate_budget(limit, reserve, margin)
    #budget = todo("입력에 쓸 수 있는 예산")
    budget = limit - (reserve + margin)
    if budget <= 0 or count(make_messages([])) > budget:
        raise ValueError("고정 입력만으로 예산을 넘었습니다.")
    kept = []
    for turn in reversed(turns):
        candidate = [turn, *kept]
        # if todo("전체 후보 입력이 예산을 넘는지"):
        if count(make_messages(candidate)) > budget:
            break
        kept = candidate
     # 관측: 전체 대화는 1999, 최근 대화와 요약+최근은 1744 토큰으로 약 250 차이가 났다.
    #       최근 대화는 T05~T07만 남기고 T01~T04가 잘려나가 담당자와 마감일이 확인 필요로 나왔다.
    #       요약+최근은 토큰은 최근 대화와 같고 정확도는 전체 대화와 같아서 이 방식을 쓴다.

    return kept


def cache_key(prefix, user_id):
    # return todo("사용자와 고정 지시로 만드는 캐시 키")
    text = user_id + "\n" + prefix
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
    # 관측: 첫 사용(두 번째)에서 쓰기 1228 토큰, 재사용(세 번째)에서 읽기 1228 토큰이 관측되었다.
    #       첫 사용은 캐시 쓰기 비용때문에 추가 비용이 들고 재사용은 캐시를 그대로 써서 비용이 적게 들었다.
    #       오염 자료 두 개는 필터에서 빠졌다.



# 선택 심화 1. 새 대화만 반영하고 변경 이력 남기기
def merge_summary(previous, turns):
    return todo("선택 심화: 새 턴의 요약과 변경 이력")


if __name__ == "__main__":
    raise SystemExit(support.cli(sys.modules[__name__]))
