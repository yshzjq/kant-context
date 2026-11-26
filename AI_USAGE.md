# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 오류 원인 확인에 사용할 수 있습니다. 과제 전체, 미작성 빈칸, 선택 심화의 설계나 정답을 대신 작성하도록 요청하지 않습니다. 설명을 이해한 뒤 직접 수정하고 다시 검사하세요.

사용하지 않았다면 아래에 사용하지 않음이라고 적습니다. 사용했다면 필요한 만큼 행을 추가하세요. API 키와 개인 정보는 기록하지 않습니다.

| 사용 도구 | 질문 | 이해한 내용 | 직접 수정한 부분 | 다시 실행한 명령과 결과 |
|---|---|---|---|---|
| Claude (Cowork) | select_context: 조건 묶는 방법 | and가 or보다 먼저 묶이므로 사용자 조건을 괄호로 감싸야 한다. priority는 사용 허락이 아니므로 먼저 걸러야 한다 | 괄호 위치와 == 비교를 지적받아 고침. 이유 주석은 직접 작성 | check context 5/5 |
| Claude (Cowork) | build_messages: 메시지 목록 구성 | history는 *로 펼쳐 넣는다. 자료를 지시와 분리하면 자료 속 문장이 지시로 취급되지 않는다 | AI가 다른 예시로 구조를 보여 준 뒤 변수를 직접 맞춰 작성. 이유 주석은 직접 작성 | check context 5/5 |
| Claude (Cowork) | memory_action: 사본과 없는 키 처리 | deepcopy로 저장소를 보호한다. get, pop(key, None)은 없으면 None | read의 get, delete의 pop(key, None) 형태는 AI가 제시한 것을 콘솔로 확인하고 반영 | check memory 4/4 |
| Claude (Cowork) | summarize, select_window, cache_key | 예산과 같으면 포함하므로 > budget일 때 멈춘다. 캐시 키는 사용자, 줄바꿈, prefix 순서의 SHA-256 | 출처 ID, 초과 조건, 해시 순서와 hexdigest 인자를 지적받아 고침 | check compare 4/4, check cache 3/3 |
| Claude (Cowork) | 관측 주석: 결과 파일 읽는 법 | 요약+최근은 토큰은 최근 대화와 같고 정확도는 전체 대화와 같다. 캐시는 첫 사용에 쓰기 비용이 든다 | AI가 수치를 표로 정리해 주었고, 문장은 질문에 답하며 직접 작성 | compare --live 일치 3/0/3, cache --live 쓰기 1228 → 읽기 1228 |
| Claude (Cowork) | AI_USAGE.md | - | AI가 대화 내용으로 초안을 쓰고 내가 확인 | - |
