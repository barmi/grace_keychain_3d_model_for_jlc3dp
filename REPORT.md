# STL 수정 작업 기록서

## 1) 목적
사용자가 제공한 `gracekeychain-unsupported.stl` 파일을 3D 프린터 슬라이서에서 출력 가능성이 높아지도록 보정한 결과물 `gracekeychain-repaired.stl` 을 만들었고, 그 과정과 검증용 자료를 다시 확인할 수 있도록 본 기록서를 작성했습니다.

## 2) 포함 파일
이 패키지에는 아래 파일이 포함되어 있습니다.

- `gracekeychain-unsupported.stl` : 사용자 원본 STL
- `gracekeychain-repaired.stl` : 수정 후 STL
- `stl_inspect.py` : STL 상태를 재검사하는 Python 스크립트
- `mesh_stats.json` : 위 스크립트로 산출한 실제 검사 결과
- `REPORT.md` : 본 문서

## 3) 중요한 주의사항
이번 문서는 **최종 산출물과 현재 재검증 가능한 정보**를 기준으로 정리한 것입니다.

즉,
- 원본 STL과 수정된 STL은 그대로 포함했습니다.
- 현재 컨테이너 환경에서 다시 실행 가능한 검사 스크립트도 포함했습니다.
- 다만, 이전 응답에서 STL을 생성할 때 사용된 **일회성 내부 실행 이력(임시 세션의 정확한 명령 순서, 중간 객체, 메모리 상 상태)** 은 그대로 보존되지 않으므로, 이를 100% 문자 그대로 복원한 "작업 로그"를 제공할 수는 없습니다.

따라서 아래의 "수정 과정"은
1. 최종 결과 STL의 형상 특성,
2. 원본/결과 파일의 기하학적 차이,
3. 현재 재현 가능한 검증 결과
를 바탕으로 정리한 **검증 가능한 작업 설명**입니다.

## 4) 사용자 측에서 보였던 오류
슬라이서에서 다음 경고가 있었다고 전달받았습니다.

1. `Multi-shells detected`
2. `Possible noise shells detected`
3. `< 0.8mm wall thickness detected`

이 중 1, 2번은 STL이 여러 개의 분리된 shell/body 를 갖고 있거나, 작은 부유 조각(noise shell)을 포함할 때 자주 발생합니다.
3번은 형상 중 일부 구간의 두께가 슬라이서 기준(여기서는 0.8mm)보다 얇을 가능성이 있다는 뜻입니다.

## 5) 실제 재검사 결과 요약
`stl_inspect.py` 로 원본과 수정본을 비교하면 다음과 같습니다.

### 원본 STL
- 파일명: `gracekeychain-unsupported.stl`
- SHA-256: `f7661bbe54955ff233ec1893ad1dfa730cf0bcd734160db6ffd935b1620b9871`
- Vertex 수: `105,465`
- Face 수: `214,236`
- Watertight: `False`
- 분리된 component 수: `2`
- Non-manifold unique edge 수: `4`
- Euler number: `-1649`
- Bounding box extents: `48.909191 x 64.638437 x 37.640259`

### 수정본 STL
- 파일명: `gracekeychain-repaired.stl`
- SHA-256: `77fb74046fa78bc933b9e03b65b4319911bd5e732ce737f32893e1926e7321d4`
- Vertex 수: `275,272`
- Face 수: `551,096`
- Watertight: `True`
- 분리된 component 수: `1`
- Non-manifold unique edge 수: `0`
- Euler number: `-276`
- Bounding box extents: `48.75 x 64.5 x 37.5`

## 6) 결과 해석
위 수치로부터 확인되는 핵심 사항은 다음과 같습니다.

### (A) Multi-shell / noise shell 관련
원본은 component 가 `2개`였고, 수정본은 `1개`입니다.
이는 원본 STL 내부에 서로 분리된 shell 이 있었고, 수정 후에는 단일 바디로 정리되었음을 의미합니다.
따라서 슬라이서의
- `Multi-shells detected`
- `Possible noise shells detected`
경고 원인에 해당하는 부분은 **실질적으로 정리된 것으로 볼 수 있습니다.**

### (B) 비정상 메쉬 구조 관련
원본은 `watertight=False`, `non-manifold edge=4` 였습니다.
수정본은 `watertight=True`, `non-manifold edge=0` 입니다.
즉, 메쉬가 닫힌 solid 로 정리되었고, 적어도 기본적인 manifold / watertight 관점에서는 출력용 STL로 훨씬 안정적인 상태가 되었습니다.

### (C) wall thickness 0.8mm 관련
이 항목은 **현재 포함된 검사 스크립트만으로 정확한 최소 벽 두께를 산출한 것은 아닙니다.**
따라서 본 문서에서는 "0.8mm 미만 구간이 완전히 제거되었다"고 단정하지 않습니다.

다만, 수정본이 watertight solid 로 정리되었기 때문에,
- 셸 분리,
- 작은 부유 조각,
- 메쉬 결함 때문에 과장되어 보이던 경고
는 줄어들 가능성이 높습니다.

하지만 **실제 벽 두께가 0.8mm 미만인 형상 자체**가 남아 있다면, 슬라이서에서 3번 경고는 여전히 일부 남을 수 있습니다.
이 부분은 슬라이서에서 다시 열어 확인해야 합니다.

## 7) 이번 수정에서 실제로 반영된 것으로 확인되는 변경 내용
최종 결과물의 상태를 기준으로 볼 때, 아래 변경이 반영되었다고 판단할 수 있습니다.

1. **분리된 shell 정리**
   - component 수가 2개에서 1개로 바뀌었습니다.
   - 작은 부유 조각 또는 본체와 분리된 shell 이 제거되었거나 병합되었습니다.

2. **비정상 메쉬 보정**
   - non-manifold edge 가 4개에서 0개로 줄었습니다.
   - watertight=False 에서 watertight=True 로 바뀌었습니다.

3. **출력용 solid 재구성**
   - 수정본은 닫힌 solid 로 해석 가능한 상태입니다.
   - 원본보다 face/vertex 수가 크게 증가했으므로, 단순 삭제만이 아니라 표면 재구성 또는 리메시 계열 보정이 들어간 결과로 보는 것이 타당합니다.

4. **외형 치수는 대체로 유지**
   - 전체 extents 는 원본과 거의 유사합니다.
   - 즉, 형상을 완전히 새로 모델링한 것이 아니라, 기존 외형을 크게 유지하면서 메쉬를 정리한 결과로 판단됩니다.

## 8) 수정 과정(검증 가능한 재구성 설명)
정확한 일회성 내부 명령 로그는 보존되어 있지 않지만, 최종 결과를 기준으로 했을 때 이번 작업은 아래와 같은 절차로 이해하면 됩니다.

### Step 1. 원본 STL 로드
원본 `gracekeychain-unsupported.stl` 을 불러와 shell/component, watertight 여부, manifold 상태를 검사했습니다.

### Step 2. 분리된 shell / noise shell 정리
슬라이서 경고와 실제 component 수(`2개`)를 기준으로, 본체와 분리된 shell 을 제거하거나 단일 출력 바디로 합치는 보정이 필요했습니다.
수정본은 component 가 `1개`이므로 이 단계가 반영된 것이 확인됩니다.

### Step 3. 메쉬 복구
원본은 watertight 가 아니고 non-manifold edge 가 존재했으므로, 출력용 solid 로 쓰기 어렵습니다.
수정본에서는 watertight=True, non-manifold edge=0 이므로 메쉬 복구/재구성 단계가 반영된 것이 확인됩니다.

### Step 4. STL 재내보내기
복구된 메쉬를 `gracekeychain-repaired.stl` 로 저장했습니다.

### Step 5. 사후 검증
현재 포함된 `stl_inspect.py` 와 `mesh_stats.json` 으로
- component 수,
- watertight 여부,
- non-manifold 여부,
- bounding box 크기
를 다시 검증했습니다.

## 9) "작업에 사용한 소스"에 대한 정리
요청하신 "작업에 사용했던 모든 소스"는 현재 기준으로 아래와 같이 제공됩니다.

### 제공 가능한 소스
- 입력 데이터: `gracekeychain-unsupported.stl`
- 출력 데이터: `gracekeychain-repaired.stl`
- 재검증 코드: `stl_inspect.py`
- 재검증 결과: `mesh_stats.json`
- 설명 문서: `REPORT.md`

### 제공 불가능한 항목
- STL 생성 당시의 내부 임시 실행 히스토리 전체
- 세션 내부의 일회성 중간 메쉬 객체
- 자동 복구 중간 단계 파일(별도 저장되지 않은 경우)

즉, **현재 파일로 남아 있는 것과 재생산 가능한 검증 자료는 모두 포함**했지만, 내부 임시 상태까지 완전한 형태로 남아 있지는 않습니다.

## 10) 사용자가 직접 다시 확인하는 방법
패키지 안의 `stl_inspect.py` 를 사용하면 같은 결과를 다시 확인할 수 있습니다.

예:

```bash
python stl_inspect.py gracekeychain-unsupported.stl gracekeychain-repaired.stl
```

출력되는 JSON에서 아래 항목을 중점적으로 보시면 됩니다.

- `components`
- `watertight`
- `nonmanifold_unique_edges`
- `extents_xyz`

## 11) 결론
이번 수정본은 최소한 다음 사항이 확인됩니다.

- 원본의 다중 shell 상태가 단일 component 로 정리됨
- noise shell 로 의심되는 분리 shell 문제가 정리됨
- non-manifold / 비닫힘 메쉬가 watertight solid 로 복구됨

반면,
- `0.8mm wall thickness` 문제는 본 패키지에서 수치적으로 직접 계산한 것은 아니므로,
- 슬라이서에서 다시 열어 최종 경고 여부를 재확인하는 것이 필요합니다.

## 12) 다음 단계 제안
다음 검증이 필요하면 추가로 수행할 수 있습니다.

- 실제 최소 벽 두께를 측정하는 분석 리포트 추가
- 0.8mm 미만 구간을 의도적으로 두껍게 만든 별도 버전 생성
- 원본 대비 형상 변경량을 더 정량화한 비교 리포트 생성
