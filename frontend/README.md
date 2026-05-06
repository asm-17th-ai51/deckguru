# DeckGuru Frontend (51조)

`frontend/`는 monorepo 내 Next.js 프론트엔드입니다. DeckGuru의 첫 화면, 덱 추천 입력 폼, 공통 UI 컴포넌트, 전역 스타일을 담당합니다.

> **이 README는 프론트엔드 초기 이관 기준입니다.**
> 현재는 메인 화면과 검색 폼 UI가 구현되어 있으며, 백엔드 추천 API 연동은 이후 작업에서 추가 예정입니다.

## 기술 스택

| 항목 | 버전 / 도구 | 설명 |
|---|---|---|
| Framework | `Next.js 16.1.7` | App Router 기반 프론트엔드 |
| Runtime UI | `React 19.2.4` | Client Component와 폼 상태 처리 |
| Language | `TypeScript 5.9.3` | strict 모드 사용 |
| Styling | `Tailwind CSS 4.2.1` | `src/app/globals.css` 중심 전역 스타일 |
| UI | `shadcn`, `@base-ui/react` | 공통 UI 컴포넌트 기반 |
| Theme | `next-themes` | 라이트/다크 테마 provider |
| Package Manager | `pnpm 10.28.2` | `frontend/pnpm-lock.yaml` 기준 |

## 디렉토리

```text
frontend/
├── package.json            # Next.js 실행 / 빌드 / 검사 스크립트
├── pnpm-lock.yaml          # 프론트엔드 의존성 lockfile
├── next.config.mjs         # Next.js 설정 (Turbopack root 포함)
├── tsconfig.json           # TypeScript + @/* alias 설정
├── eslint.config.mjs       # ESLint 설정
├── postcss.config.mjs      # Tailwind CSS 4 PostCSS 설정
├── components.json         # shadcn UI 설정
├── public/                 # PWA manifest 이미지 등 정적 파일
└── src/
    ├── app/
    │   ├── layout.tsx      # 루트 레이아웃 + ThemeProvider + 폰트 설정
    │   ├── globals.css     # Tailwind CSS 4 전역 스타일 / 디자인 토큰
    │   ├── manifest.json   # 앱 manifest
    │   └── (main)/
    │       └── page.tsx    # 메인 화면 / 덱 추천 입력 폼
    ├── components/
    │   ├── providers/      # 전역 provider
    │   └── ui/             # Button, Input 등 공통 UI
    ├── assets/
    │   └── fonts/          # Galmuri 폰트 로딩
    ├── hooks/              # 공통 React hook 확장 위치
    └── lib/
        └── utils.ts        # className 병합 유틸
```

## 셋업

### 사전 준비

`frontend/`는 Next.js 16 기준으로 Node.js `20.9.0` 이상이 필요합니다. 현재 lockfile은 pnpm `10.28.2` 기준입니다.

```bash
# Node.js 버전 확인
node -v

# pnpm 버전 확인
pnpm -v
```

Node.js가 없거나 버전이 낮으면 다음 중 하나로 설치합니다.

```bash
# Homebrew 사용
brew install node

# nvm 사용
nvm install 20
nvm use 20
```

pnpm이 없으면 Corepack으로 활성화합니다.

```bash
corepack enable
corepack prepare pnpm@10.28.2 --activate
```

### 실행

```bash
# monorepo 루트에서 이동
cd frontend

# 의존성 설치
pnpm install

# 개발 서버 실행
pnpm dev
```

기본 개발 서버 주소는 다음과 같습니다.

```text
http://localhost:3000
```

## 환경변수

현재 프론트엔드는 필수 환경변수를 사용하지 않습니다.

백엔드 API 연동이 추가되면 다음 형태의 공개 환경변수를 사용할 예정입니다.

| 변수 | 기본값 | 설명 |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | (미정) | FastAPI gateway base URL |

## 스크립트

```bash
# 개발 서버 실행
pnpm dev

# 프로덕션 빌드
pnpm build

# 빌드 결과 실행
pnpm start

# ESLint 검사
pnpm lint

# TypeScript 타입 검사
pnpm typecheck

# Prettier 포맷
pnpm format
```

## 테스트 / 검증

현재 별도 테스트 러너는 설정되어 있지 않습니다. 프론트엔드 변경 후 최소한 다음 명령을 실행합니다.

```bash
pnpm lint
pnpm typecheck
pnpm build
```

개발 서버에서 화면까지 확인하려면 다음 명령을 사용합니다.

```bash
pnpm dev
```

브라우저에서 `http://localhost:3000`에 접속해 메인 화면과 검색 폼 렌더링을 확인합니다.
