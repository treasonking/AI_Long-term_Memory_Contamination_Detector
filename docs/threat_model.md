# Threat Model

## 1. 보호 대상

- Agent long-term memory
- 사용자 선호 정보
- 보안 정책 관련 memory
- 도구 사용 관련 memory
- 문서 검색 우선순위 memory

## 2. 공격자 모델

- 악성 웹페이지 작성자
- 악성 이메일 발신자
- 외부 문서 작성자
- tool output을 조작할 수 있는 공격자
- 낮은 권한의 내부 사용자

## 3. 공격 경로

- Indirect prompt injection
- Poisoned document
- Malicious webpage
- Malicious email
- Manipulated tool output
- Cross-agent propagation

## 4. 보안 목표

- 악성 memory 저장 차단
- 이미 저장된 memory 정기 스캔
- 위험 memory 격리
- 변경 이력 추적
- 오염 전후 행동 변화 재현

## 5. 비목표

- 실제 LLM 모델 해킹
- 실제 사용자 계정 탈취
- 실제 외부 서버 유출
- 상용 서비스 메모리 직접 조작
