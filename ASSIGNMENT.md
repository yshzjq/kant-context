# 입력과 기억 관리

KANT NEXT의 DevDesk는 개발팀의 문서와 대화를 바탕으로 업무 상태를 안내합니다. 오래된 기억과 확인하지 않은 자료를 제외하고, 대화가 길어져도 현재 담당자와 승인조건을 놓치지 않도록 개선해 주세요.

필수 2문제와 선택 심화 1문제입니다. 필수에서는 `main.py`의 작은 빈칸 10곳을 채웁니다. 반복문, 파일 저장, API 연결과 결과 기록은 제공됩니다. 필수 구현을 마친 뒤 선택 심화에 도전하세요.

환경 준비는 [시작 가이드](README.md), 입력 필드는 [제공 자료 안내](data/DATA_CARD.md)에서 확인하세요. 아래 예시는 동작 설명용이며 제공된 `data/`를 바꾸는 작업이 아닙니다.

## 필수 1. 필요한 자료와 사용자 기억 관리하기

다른 사람의 기억이나 만료된 안내는 질문과 관련 있어도 사용하면 안 됩니다. 사용할 자료를 고르고, 지시와 참고 자료를 나눈 뒤 사용자별 기억을 저장하고 다시 읽는 기능을 완성하세요.

먼저 `select_context`로 남길 자료를 확인한 뒤 그 결과를 `build_messages`에 넣어 메시지 순서를 확인하세요. 두 함수가 동작하면 `memory_action`의 저장, 조회, 수정, 삭제를 완성합니다. 파일에서 읽은 기억을 자료 형식으로 바꾸고 이 두 함수에 연결하는 부분은 제공 코드가 담당합니다.

### 사용할 자료 선택: `select_context`

`select_context(items, user_id, now)`의 `allowed` 조건을 작성합니다. 아래 조건을 모두 만족한 항목만 남깁니다.

- `user_id`가 `public` 또는 현재 사용자입니다.
- `trusted`와 `active`가 모두 `True`입니다.
- `expires_at`이 `None`이거나 기준일 `now`보다 뒤입니다. 만료일 당일부터 제외합니다.

날짜는 모두 `YYYY-MM-DD` 형식이므로 이 과제에서는 문자열 순서로 비교할 수 있습니다.

제공되는 부분: 원본의 사본 만들기와 정렬. 높은 `priority`부터, 동점이면 ID 오름차순입니다.

> 참고: `trusted`는 서비스가 미리 검토한 메타데이터입니다. 본문이 스스로 주장한 값이 아니며, 이 조건만으로 새로운 공격을 모두 탐지하지는 못합니다.

#### 작은 예시

현재 사용자가 `sora`, 기준일이 `2026-11-04`이고 세 자료의 `trusted`, `active`가 모두 `True`라고 합시다. 다른 필드는 생략했습니다.

| id | user_id | expires_at | priority |
|---|---|---|---:|
| `policy` | `public` | `None` | 1 |
| `other-note` | `yujin` | `None` | 99 |
| `expired-note` | `sora` | `2026-11-04` | 99 |

남는 ID는 `policy` 하나입니다. 다른 사람의 기억과 오늘 만료된 기억은 우선순위가 높아도 제외합니다.

### 메시지 조립: `build_messages`

`build_messages(prefix, question, context, turns, summary)`의 반환 목록을 작성합니다. `data`는 자료와 요약을 담은 JSON 문자열이며 `history`는 제공 코드가 풀어 놓은 대화 메시지 목록입니다.

| 순서 | role | content |
|---|---|---|
| 맨 앞 | `developer` | `prefix` |
| 다음 | `user` | `data` |
| 그다음 | 기존 역할 유지 | `history`의 메시지들 |
| 맨 뒤 | `user` | `question` |

앞 예시의 선택 자료와 빈 `turns`, 빈 `summary`를 전달하면 메시지는 세 개입니다. 역할은 `developer`, `user`, `user` 순서이며, 가운데 메시지의 `reference_data`에는 `policy`만 들어갑니다.

검색 문서와 도구 결과의 `kind`는 자료 종류입니다. 실제 API 도구 호출이 없으므로 `tool` 역할 메시지를 만들지 않습니다. 자료 본문을 `developer` 지시로 올리지 마세요. `select_context`의 이유 주석에 우선순위보다 사용 가능 여부를 먼저 확인하는 이유를 적습니다.

### 기억의 저장, 조회, 수정, 삭제: `memory_action`

`memory_action(records, user_id, action, name, value=None)`의 네 빈칸을 작성합니다. `records`는 기억 저장소의 내용, `key`는 현재 사용자와 기억 이름을 결합한 키입니다. 파일 읽기와 저장은 제공 코드가 담당합니다.

| action | 작성할 동작 | 없는 항목의 처리 |
|---|---|---|
| `read` | `key`의 값을 사본으로 반환 | `None` |
| `create` | `key`에 `value`의 사본 저장 | 새로 저장 |
| `update` | 기존 `key`의 값을 `value`의 사본으로 교체 | 제공 코드가 `KeyError` |
| `delete` | `key`의 항목을 제거하고 제거한 값을 반환 | `None` |

`copy.deepcopy()`를 사용하면 중첩 사전의 사본을 만들 수 있습니다. 조회한 사전을 바꿨다고 저장소의 값까지 바뀌면 안 됩니다. 같은 사용자의 같은 이름을 중복 생성하면 제공 코드가 오류를 냅니다.

제공 코드는 두 저장소를 분리합니다.

| 저장소 | 용도와 수명 |
|---|---|
| `style` | 동의를 받은 가상의 장기 선호. JSON 파일에 저장하고 다시 읽음 |
| `task` | 현재 세션의 작업 메모. 세션이 끝나면 비움 |

`run memory`는 저장소를 다시 연 뒤 민지의 선호를 수정하고 삭제합니다. 지훈의 선호는 남아 있어야 합니다.

> 참고: 이 예제의 삭제는 활성 JSON 항목의 삭제이며 백업이나 모든 보존본 삭제를 뜻하지 않습니다.

`build_messages`의 이유 주석에 장기 기억과 세션 상태의 차이, 자료와 지시를 나누는 이유를 한두 문장으로 남기세요.

### 실행과 확인

```text
uv run --frozen python main.py run context
uv run --frozen python main.py check context
uv run --frozen python main.py run memory
uv run --frozen python main.py check memory
```

선택 자료가 현행 정책, 확인된 조회 결과, 민지의 유효한 선호인지 확인합니다. `run memory`는 파일에서 읽은 기억을 자료 선택과 메시지 조립에도 연결합니다. 결과 파일은 `artifacts/context-fixture.json`과 `artifacts/memory-fixture.json`입니다. `messages_before`, `messages_after`, `messages_deleted`에서 민지의 설명 방식이 수정되고 삭제되는지, 지훈의 기억은 입력에 없는지 확인하세요.

`artifacts/memory.json`은 실행 중 생성되는 테스트 기억입니다. `run memory`를 다시 실행하면 제공 예제로 초기화되므로 개인정보를 넣지 마세요.

## 필수 2. 긴 대화를 줄이고 반복 입력 재사용하기

최근 대화만 남기면 앞에서 정한 승인조건이 사라질 수 있습니다. 최신 사실을 요약해 남기고, 남은 공간에는 최근의 연속된 대화만 넣으세요. 공통 지시를 앞에 유지한 요청의 캐시 동작도 확인합니다.

요약과 최근 대화를 함께 쓰는 흐름부터 살펴보세요. 전체 대화에서 `summarize`로 사실을 정리하고, 그 요약이 포함된 입력을 기준으로 `select_window`가 남길 턴을 고릅니다. 제공 코드가 마지막에 `build_messages`로 요약과 선택한 턴을 합칩니다. 이 흐름을 확인한 뒤 같은 공통 지시를 재사용하는 캐시 키를 작성하세요.

### 최신 사실 요약: `summarize`

`summarize(turns)`의 빈칸에서 각 항목에 `value`와 `source_turn_id`를 담은 사전을 저장하세요.

- 같은 항목이 다시 나오면 최신 값으로 교체합니다.
- 다시 나오지 않은 항목은 남겨 둡니다.

제공되는 부분: 오래된 턴부터 사용자 발화의 담당자, 마감일, 승인조건을 읽는 반복문. 어시스턴트의 추측과 빈 값은 제공 함수가 제외합니다.

#### 작은 예시

세 턴의 사용자 발화가 아래와 같고 어시스턴트는 각각 확인했다고만 답했다고 합시다.

| 턴 ID | 사용자 발화 |
|---|---|
| `A01` | `담당자: 김소라` |
| `A02` | `승인조건: 팀장 확인` |
| `A03` | `담당자: 박유진` |

요약 결과에는 최신 담당자와 앞서 정한 승인조건이 함께 남습니다.

```json
{
  "담당자": {"value": "박유진", "source_turn_id": "A03"},
  "승인조건": {"value": "팀장 확인", "source_turn_id": "A02"}
}
```

### 입력 예산에 맞는 대화 선택: `select_window`

`select_window(...)`의 예산 계산과 초과 조건을 작성합니다.

1. 입력 예산은 `limit`에서 `reserve`와 `margin`을 뺀 값입니다.
2. 각 `candidate`에 대해 `make_messages(candidate)`로 전체 메시지를 만들고 `count()`로 셉니다.
3. 예산을 넘으면 반복문을 멈춥니다. 예산과 같으면 포함합니다. 넘친 턴을 건너뛰고 더 오래된 턴을 추가하지 않습니다.

고정 지시, 자료, 요약, 현재 질문도 예산에 포함됩니다. 사용자와 어시스턴트 메시지는 한 턴으로 함께 남깁니다. 고정 입력만으로 예산을 넘으면 제공 코드가 오류를 냅니다.

`make_messages`는 후보 턴 목록을 받아 필수 1의 `build_messages`로 전체 입력을 만드는 제공 함수이고, `count`는 그 입력의 토큰 수를 세는 함수입니다. 두 함수를 새로 구현할 필요는 없습니다.

#### 작은 예시

`limit=12`, `reserve=3`, `margin=2`라면 입력 예산은 7입니다. 아래 수치는 선택 순서를 설명하는 가정값이며 실제 API 측정값이 아닙니다.

| 포함한 내용 | 입력 크기 | 처리 |
|---|---|---|
| 요약을 포함한 고정 입력 | 4 | 기본 입력 |
| 고정 입력 + `A03` | 7 | 예산과 같으므로 포함 |
| 고정 입력 + `A02`, `A03` | 12 | 예산을 넘으므로 중단 |

남길 턴은 `A03`뿐이며 `A01`을 따로 넣지 않습니다. `A02`의 원문 대화가 빠져도 앞에서 만든 요약에 승인조건이 남습니다.

> 참고: `count()`는 `o200k_base` 인코딩으로 직렬화한 메시지를 세는 비교용 추정 함수입니다. 실제 API의 메시지 처리와 완전히 같지는 않습니다. 출력 384와 안전 여유 128을 별도로 남기며, 실제 사용량은 `--live`의 `usage`에서 확인합니다. 이 과제의 한도 2,300과 5,000은 실험 설정으로, 모델 자체의 최대 길이가 아닙니다.

#### 실행과 확인

[시작 가이드의 실제 연결 준비](README.md#실제-연결-준비)에서 API 키를 설정하세요. 아래 실제 비교는 모델을 3회 호출합니다.

```text
uv run --frozen python main.py run compare
uv run --frozen python main.py check compare
uv run --frozen python main.py run compare --live
```

전체 대화, 최근 대화, 요약과 최근 대화의 세 조건을 비교합니다. 결과는 `artifacts/compare-fixture.json`과 `artifacts/compare-live.json`에 저장됩니다. `estimated_input_tokens`, 남긴 턴, 실제 답변을 확인하세요. `exact_fields`는 제공한 사실 3개의 문자열 완전 일치 수입니다. 같은 뜻의 다른 문장도 불일치할 수 있으므로 실제 답변은 대화 원문과 직접 대조합니다. 고정 예제의 함수 응답은 모델 품질 측정이 아닙니다.

`select_window`의 관측 주석에 토큰 수와 빠진 사실, 세 방식 중 사용할 방식을 적고 그 이유를 한두 문장으로 설명하세요. 실제 실행을 못 했다면 고정 예제에서 확인한 범위와 실패 상황을 구분합니다.

### 반복 입력의 캐시 키: `cache_key`

`cache_key(prefix, user_id)`의 반환값을 작성하세요.

- 사용자 ID, 줄바꿈 하나, Prefix를 순서대로 합칩니다. 질문과 요청 시각은 넣지 않습니다.
- 합친 문자열의 UTF-8 SHA-256 16진수 값을 반환합니다. `hashlib.sha256(...).hexdigest()`를 활용할 수 있습니다.
- 같은 사용자와 같은 지시는 같은 키를, 사용자나 지시가 달라지면 다른 키를 만듭니다.

`build_messages`에서 공통 지시를 첫 메시지로 두었으므로 질문과 검색 자료가 달라져도 앞부분이 유지됩니다. 실제 전송 코드는 그 지시 끝에 명시적인 캐시 경계를 붙입니다. GPT-5.6 계열에서 키는 사용자별 캐시 계량을 구분하며, 키만 같다고 적중이 보장되지는 않습니다.

#### 실행과 확인

```text
uv run --frozen python main.py run cache
uv run --frozen python main.py check cache
uv run --frozen python main.py run cache --live
```

실제 실행은 같은 요청을 캐시 비사용, 이번 실행의 첫 사용, 재사용 순서로 3회 호출합니다. 결과는 `artifacts/cache-fixture.json`과 `artifacts/cache-live.json`에 저장됩니다. `cached_tokens`, `cache_write_tokens`, `actual_input_cost_usd`, `latency_ms`를 비교하세요. 이전 실행의 캐시가 남아 있으면 첫 사용부터 읽기가 나올 수 있습니다. 캐시 쓰기도 비용이 있으며, 첫 쓰기 때문에 항상 더 저렴한 것은 아닙니다. 읽기 0과 계량 누락도 구분합니다. 한 번의 지연 차이만으로 일반적인 속도 향상을 단정하지 마세요.

`cache_key`의 관측 주석에 확인한 읽기/쓰기 토큰과 비용 차이를 적습니다. 관측되지 않았다면 그렇게 적고, 필터에서 제외한 오염 자료 두 개가 최종 입력에 없는지도 함께 확인하세요. 가격의 출처와 확인일은 `data/prices.json`에 있습니다.

## 선택 심화 1. 새 대화만 반영하고 변경 이력 남기기

매번 처음부터 요약하지 않고 새로 도착한 턴만 반영합니다.

### 구현 조건: `merge_summary`

새로 도착한 턴만 반영하는 `merge_summary(previous, turns)`를 작성하세요. 필수 `summarize`의 판단을 재사용하되 아래 반환 구조를 유지합니다.

먼저 최신 사실이 필수 요약과 같은 모양으로 남는지 확인하고, 변경 이력과 처리한 턴 ID를 각각 점검하세요. `current`는 지금 사용할 사실, `changes`는 값이 바뀐 기록, `processed_ids`는 이미 읽은 턴의 목록입니다.

```json
{"current": {}, "changes": [], "processed_ids": []}
```

`current`는 필수 요약과 같은 구조입니다. 항목의 값이 바뀌면 `changes`에 `name`, `before`, `after`를 담습니다. `before`와 `after`에는 각각 값과 출처 턴 ID가 있어야 합니다. 새 항목이나 같은 값의 재확인은 변경 이력을 만들지 않지만 최신 출처 턴은 반영합니다.

이미 `processed_ids`에 있는 턴은 건너뜁니다. 처음 처리한 턴은 입력 순서대로 ID를 추가합니다. 사실이 없는 턴도 처리한 것으로 남깁니다. 입력은 시간순이며 턴 ID는 원본 대화를 식별합니다. 같은 ID의 본문이 나중에 바뀌는 정정 처리는 이번 범위에 없습니다. `previous`와 `turns`를 직접 바꾸지 마세요.

### 작은 예시

아래는 두 인자에 전달할 작은 입력입니다. `S01`까지 읽은 상태에서 `S02`, `S03`이 새로 도착했습니다. 각 턴의 `messages`는 사용자 발화와 어시스턴트 답변의 쌍입니다.

```json
{
  "previous": {
    "current": {"담당자": {"value": "김소라", "source_turn_id": "S01"}},
    "changes": [],
    "processed_ids": ["S01"]
  },
  "turns": [
    {"id": "S02", "messages": [
      {"role": "user", "content": "담당자: 김소라\n마감일: 2026-11-20"},
      {"role": "assistant", "content": "확인했습니다."}
    ]},
    {"id": "S03", "messages": [
      {"role": "user", "content": "담당자: 박유진"},
      {"role": "assistant", "content": "확인했습니다."}
    ]}
  ]
}
```

| 상황 | 기대하는 변화 |
|---|---|
| 새 항목: `S02`의 마감일 | `current`에 값 `2026-11-20`과 출처 `S02`가 생깁니다. 이력은 추가하지 않습니다. |
| 같은 값 재확인: `S02`의 담당자 | 값은 김소라로 유지하고 출처만 `S02`로 바꿉니다. 이력은 추가하지 않습니다. |
| 값 변경: `S03`의 담당자 | 값과 출처를 박유진, `S03`으로 바꾸고 변경 이력 하나를 남깁니다. |
| 재처리: 위 결과에 같은 `turns`를 다시 전달 | 요약, 이력과 처리 ID 목록이 모두 그대로입니다. |

최종 `processed_ids`는 `["S01", "S02", "S03"]`이며 `changes`에는 아래 항목 하나만 있습니다. 변경 전 출처가 최초의 `S01`이 아니라 재확인한 `S02`라는 점을 확인하세요.

```json
{
  "name": "담당자",
  "before": {"value": "김소라", "source_turn_id": "S02"},
  "after": {"value": "박유진", "source_turn_id": "S03"}
}
```

### 실행과 확인

아래 명령은 제공된 `data/scenario.json`의 대화로 실행합니다.

```text
uv run --frozen python main.py challenge
uv run --frozen python main.py check challenge
```

담당자와 마감일의 변경은 남고 승인조건은 유지되는지 확인합니다. 같은 턴을 다시 넣어도 결과가 바뀌지 않아야 합니다. 선택 심화에는 실제 API 호출이 필요하지 않습니다.

## 제출 전 확인

필수 1의 자료와 기억, 필수 2의 실제 답변과 캐시 결과를 확인하고 지정된 주석을 작성했으면 [시작 가이드의 제출 안내](README.md#제출)를 따르세요. 선택 심화는 필수 완료 조건에 포함되지 않습니다.
