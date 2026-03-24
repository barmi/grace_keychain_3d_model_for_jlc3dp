# STL Repair Reproduction Report

## 목적
원본 STL을 Python 코드만으로 수정하고, 다시 같은 코드를 실행했을 때 동일한 수정 STL이 재생성되는지 검증했습니다.

## 포함 파일
- `repair_stl.py`: 원본 STL -> 수정 STL 변환 코드
- `validate_repair.py`: 동일 코드 재실행 및 검증 코드
- `gracekeychain-repaired-reference.stl`: 이번에 코드로 생성한 기준 결과
- `gracekeychain-repaired-regenerated.stl`: 검증 코드가 다시 생성한 결과
- `repair_summary.json`: 1차 생성 결과
- `validation_report.json`: 재생성 검증 결과

## 사용한 방법
1. 원본 STL 로드
2. 연결 컴포넌트 분리
3. 너무 작은 분리 쉘 제거
4. 남은 형상을 병합
5. 0.25 mm pitch로 voxelize
6. 내부를 채워 solid화
7. marching cubes로 watertight surface 재생성
8. STL export

## 핵심 결과
### 원본
- vertices: 105465
- faces: 214236
- watertight: False
- components: 2
- euler number: -1649

### 제거된 작은 쉘
[
  {
    "index": 1,
    "vertices": 3,
    "faces": 2,
    "watertight": true,
    "bounds_min": [
      -1.609431505203247,
      12.768380165100098,
      5.672758102416992
    ],
    "bounds_max": [
      -1.5284655094146729,
      12.805032730102539,
      5.830598831176758
    ]
  }
]

### 수정 후
- vertices: 288494
- faces: 580716
- watertight: True
- components: 1
- euler number: -1864

### voxel 정보
- pitch: 0.25
- shape: [197, 260, 152]
- filled_voxel_count: 458161
- connected_components: 1

## 재현 검증
- reference sha256: 985d624d1b75ed245bd8d935c70e43873572debc154f05d402c807ce61b735b4
- regenerated sha256: 985d624d1b75ed245bd8d935c70e43873572debc154f05d402c807ce61b735b4
- exact hash match: True

### 기준 결과 vs 재생성 결과의 샘플 거리
- reference -> regenerated mean: 0.000000000000
- reference -> regenerated max: 0.000000000000
- regenerated -> reference mean: 0.000000000000
- regenerated -> reference max: 0.000000000000

해시가 동일하므로, 이번 패키지에 포함된 Python 코드로 기준 결과 STL을 다시 생성할 수 있음을 확인했습니다.

## 이전 세션 결과와의 참고 비교
- previous repaired sha256: 77fb74046fa78bc933b9e03b65b4319911bd5e732ce737f32893e1926e7321d4
- previous -> generated mean: 0.717976420752
- previous -> generated max: 1.922743289465
- generated -> previous mean: 0.727824702261
- generated -> previous max: 2.007799664239

## 실행 예시
```bash
python repair_stl.py gracekeychain-unsupported.stl out.stl --summary out.json
python validate_repair.py gracekeychain-unsupported.stl gracekeychain-repaired-reference.stl regenerated.stl --json validation_report.json
```

## 주의
이 방법은 삼각형 메쉬를 직접 봉합하는 것이 아니라 voxel 기반으로 solid를 재구성하는 방식입니다.
따라서 매우 미세한 표면은 0.25 mm 격자 기준으로 약간 변형될 수 있습니다.
하지만 multi-shell / noise shell / 비폐합 메쉬를 출력 가능한 watertight STL로 재구성하는 데에는 유리합니다.
