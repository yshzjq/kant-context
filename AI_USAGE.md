# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 오류 원인 확인에 사용할 수 있습니다. 과제 전체, 미작성 빈칸, 선택 심화의 설계나 정답을 대신 작성하도록 요청하지 않습니다. 설명을 이해한 뒤 직접 수정하고 다시 검사하세요.

사용하지 않았다면 아래에 사용하지 않음이라고 적습니다. 사용했다면 필요한 만큼 행을 추가하세요. API 키와 개인 정보는 기록하지 않습니다.

| 사용 도구 | 질문 | 이해한 내용 | 직접 수정한 부분 | 다시 실행한 명령과 결과 |
|---|---|---|---|---|
| Claude (Cowork) | select_context: 여러 조건을 묶는 방법, any()와 and/or의 차이 | or와 and가 섞이면 and가 먼저 묶이므로 사용자 조건을 괄호로 감싸야 public 자료도 trusted, active, 만료 검사를 받는다. 만료일은 문자열 비교로 > now를 써야 당일이 제외된다. | 괄호 없이 작성한 조건을 AI 지적 후 (A or B) and C and D and (E or F) 형태로 고침. user_id in 비교를 == 비교로 바꿈 | run context: release-policy, ticket-result, my-style 선택 / check context 5/5 통과 |
| Claude (Cowork) | select_context 이유 주석의 질문 의미 | priority는 쓸 수 있는 자료끼리의 순서이고 사용 허락이 아니므로 먼저 걸러야 한다. | 이유 주석을 직접 작성함 | - |
| Claude (Cowork) | build_messages: 메시지 목록 구성, 리스트 펼치기(*) | data는 자료와 요약을 담은 문자열, history는 펼쳐서 넣어야 하는 메시지 리스트다. 자료를 지시와 분리하면 자료 속 문장이 지시로 취급되지 않는다. | AI가 식당 주문 예시로 구조를 보여 준 뒤, 변수 짝(prefix, data, history, question)을 직접 맞춰 작성함. data["context"]와 쉼표 누락을 지적받아 고침. 이유 주석은 질문에 답하며 직접 작성함 | check context 5/5 통과 |
| Claude (Cowork) | memory_action: 사본이 필요한 이유, 없는 키 처리 | 같은 사전을 공유하면 바깥 수정이 저장소까지 바뀌므로 deepcopy가 필요하다. get은 없으면 None, pop(key, None)은 지우면서 값을 돌려주고 없으면 None이다. | 전체 records 반환, records[key].pop() 등을 지적받아 고침. read의 get 사용과 delete의 records.pop(key, None) 형태는 AI가 제시한 것을 콘솔 예시로 확인하고 반영함 | run memory / check memory 4/4 통과 |
| Claude (Cowork) | summarize, select_window: 출처 턴 ID, 예산 초과 조건 | 오래된 턴부터 덮어쓰므로 같은 항목은 최신 값만 남는다. 예산과 같으면 포함하므로 > budget일 때만 멈춘다. | turn 전체 대신 turn["id"], budget < 0 대신 count(make_messages(candidate)) > budget으로 고침 | run compare / check compare 4/4 통과 |
| Claude (Cowork) | cache_key: 해시 만드는 방법 | 사용자 ID, 줄바꿈, prefix 순서로 이은 문자열의 SHA-256 16진수가 키다. hexdigest는 인자를 받지 않는다. | 사전 반환, 순서 반대, hexdigest(text)를 지적받아 고침 | run cache / check cache 3/3 통과 |
| Claude (Cowork) | AuthenticationError 401 원인, Git 설정 | 시스템 환경 변수에 키가 있으면 override=False 때문에 .env 키가 무시된다. | 키 설정을 직접 확인하고 해결함. .gitignore는 AI가 작성함 | run compare --live, run cache --live 성공 |
| Claude (Cowork) | select_window, cache_key 관측 주석: 결과 파일 읽는 법 | 최근 대화는 T01~T04가 잘려 담당자와 마감일을 잃었고, 요약+최근은 토큰은 최근 대화와 같고 정확도는 전체 대화와 같다. 캐시는 첫 사용에 쓰기 비용이 들고 재사용에서 비용이 줄었다. | AI가 결과 수치를 표로 정리하고 질문을 던졌으며, 문장은 질문에 답하며 직접 작성함 | compare-live: 1999/1744/1744 토큰, 일치 3/0/3 / cache-live: 쓰기 1228(2회차), 읽기 1228(3회차), 입력 비용 0.000307→0.000368→0.000086 USD |
| Claude (Cowork) | AI_USAGE.md 작성 | - | 대화 내용을 바탕으로 AI가 초안을 쓰고 내가 확인함 | - |
