# Changelog

## [2.0.2](https://github.com/leonardokr/leo-git-statistics/compare/v2.0.1...v2.0.2) (2026-02-18)


### Bug Fixes

* resolve pybreaker NameError for tornado.gen on Python 3.12+ ([753e62b](https://github.com/leonardokr/leo-git-statistics/commit/753e62b8e3b64eef0a8e1f1f1dfbff78fcdbd386))

## [2.0.1](https://github.com/leonardokr/leo-git-statistics/compare/v2.0.0...v2.0.1) (2026-02-18)


### Bug Fixes

* pin Python 3.13.2 for pybreaker compatibility ([442b7aa](https://github.com/leonardokr/leo-git-statistics/commit/442b7aae884ee84b6932da4be0115b0c0d16a840))

## [2.0.0](https://github.com/leonardokr/leo-git-statistics/compare/v1.1.0...v2.0.0) (2026-02-18)


### ⚠ BREAKING CHANGES

* Flask replaced by FastAPI; app entrypoint moved from api/app.py to api/main.py; default port changed from 5000 to 8000

### Features

* add API key authentication with configurable enforcement ([baedfa2](https://github.com/leonardokr/leo-git-statistics/commit/baedfa20c4161c6cdd6cc1f6aa8ce9c6f4b34f5b))
* add daily stats snapshot GitHub Actions workflow ([1bbc706](https://github.com/leonardokr/leo-git-statistics/commit/1bbc706df0fac14dd5bfcf059960eac5d0c488dd))
* add Dockerfile, docker-compose.yml and .dockerignore for containerized deployment ([eb1a699](https://github.com/leonardokr/leo-git-statistics/commit/eb1a6992362f07120b51d5b4fa197d64860066c1))
* add followers and following collection via GraphQL ([e63bdea](https://github.com/leonardokr/leo-git-statistics/commit/e63bdea0d58b0257205961db54e72f050d20cda3))
* add gunicorn production server and configure workers ([8b6e466](https://github.com/leonardokr/leo-git-statistics/commit/8b6e466c99dff12cddf765f48615e12fbe2e780b))
* add in-memory TTL cache for API responses ([77fa5db](https://github.com/leonardokr/leo-git-statistics/commit/77fa5db21df34fc783317f9f26c376cc87932a93))
* add input validation with Pydantic models and username regex ([4d415d3](https://github.com/leonardokr/leo-git-statistics/commit/4d415d3d8d5a858bf96e52cb65a23828c6f08805))
* add line chart theme support with calendar color fallbacks ([e8ccb88](https://github.com/leonardokr/leo-git-statistics/commit/e8ccb88419ed18ec807beb2904048d285debc474))
* add pagination to repositories and repositories/detailed endpoints ([96a3060](https://github.com/leonardokr/leo-git-statistics/commit/96a3060bdd1cdd2c26e657523d775e6b330ef1c0))
* add partial responses with warnings on collector failure ([1474cb9](https://github.com/leonardokr/leo-git-statistics/commit/1474cb9fb186c46767960f2141d6cdb755abfb05))
* add Prometheus metrics with /metrics endpoint and custom gauges ([ae57508](https://github.com/leonardokr/leo-git-statistics/commit/ae575089d7f24f31418329c96f582f9ffa3e376f))
* add rate limiting per IP and API key with slowapi ([dd56442](https://github.com/leonardokr/leo-git-statistics/commit/dd564425ef687c088382764b57a39b9861ca61e2))
* add Redis cache backend with in-memory TTLCache fallback ([6efc7ef](https://github.com/leonardokr/leo-git-statistics/commit/6efc7ef805f86a36ed6241662fc7cc4652a93131))
* add retry with backoff, circuit breaker and rate limit monitoring to GitHubClient ([32a5938](https://github.com/leonardokr/leo-git-statistics/commit/32a5938a17cd06c8724da58c1e6f8c2f6525d29c))
* add robust health check with subsystem probes and degraded status ([73fe9a3](https://github.com/leonardokr/leo-git-statistics/commit/73fe9a3c0f4bf6c7a9a0979f0ee369ab928befde))
* add stats history multi-series line chart generator ([22b2fc8](https://github.com/leonardokr/leo-git-statistics/commit/22b2fc84931b6836d815ff9e362f515aea8e7507))
* add structured logging with structlog and request ID propagation ([a65d983](https://github.com/leonardokr/leo-git-statistics/commit/a65d983adb38d97dd5d76f1a89ed8cf96f76ab36))
* add SVG card endpoints with theme support via /users/{username}/cards/{type} ([5e6f78e](https://github.com/leonardokr/leo-git-statistics/commit/5e6f78e7309a2537b6a3c538dc450cd1863fb9cf))
* add temporal statistics snapshots with SQLite storage and history endpoint ([94859e2](https://github.com/leonardokr/leo-git-statistics/commit/94859e28d9ed98416f0ee7abac142f609fb62685))
* add user comparison endpoint at /users/{username}/compare/{other} ([f2e24e5](https://github.com/leonardokr/leo-git-statistics/commit/f2e24e5228cc8cc7b0cc20619e6ad9adc89b7b7a))
* add webhook registration and notification dispatch on snapshot triggers ([e6817e2](https://github.com/leonardokr/leo-git-statistics/commit/e6817e28c564e8327f07fa381ba609f258f69928))
* isolate server token to exclude private repos by default ([50fbae0](https://github.com/leonardokr/leo-git-statistics/commit/50fbae08b3e66009733b29caac2fc2ab8e54bd1f))
* migrate API from Flask to FastAPI with modular structure ([7ecbea2](https://github.com/leonardokr/leo-git-statistics/commit/7ecbea271cca915d249495b167eb4994e4e86029))
* register cards, compare, history and webhooks routers in main app ([39bfacc](https://github.com/leonardokr/leo-git-statistics/commit/39bfaccb7ffa4714a7af8557ccfb689b04f9e61b))
* support user-supplied GitHub token via X-GitHub-Token header ([b8d251c](https://github.com/leonardokr/leo-git-statistics/commit/b8d251c79c4e4880cfdfedacff106eb266a4c98e))


### Bug Fixes

* add tzdata to requirements for Windows timezone support ([11745cc](https://github.com/leonardokr/leo-git-statistics/commit/11745cc61a496476f3d20cd453c4731b971300ce))


### Performance Improvements

* parallelize repository API calls with asyncio.gather and semaphore ([5ca9582](https://github.com/leonardokr/leo-git-statistics/commit/5ca958236b7998c4bb18c5b9b16271a2b18549f7))
* use persistent event loop, shared aiohttp session, and TTL cache in all routes ([b6370ec](https://github.com/leonardokr/leo-git-statistics/commit/b6370ecef392e46a394e61b862803f3dcdf5c966))

## [1.1.0](https://github.com/leonardokr/leo-git-statistics/compare/v1.0.1...v1.1.0) (2026-02-17)


### Features

* add API environment configuration template with PAT generation instructions ([79f56f7](https://github.com/leonardokr/leo-git-statistics/commit/79f56f7361b1003676984f4fe4328ed906ea0b95))
* add Flask API dependencies ([3f4a117](https://github.com/leonardokr/leo-git-statistics/commit/3f4a117cf620486f663f131d62fafe786b511bd3))
* add REST API with Swagger documentation and user statistics endpoints ([7f71325](https://github.com/leonardokr/leo-git-statistics/commit/7f7132573ce914b857ea0d6bcc26d9f61c43af71))
* add static JSON generator for GitHub Pages deployment ([693c997](https://github.com/leonardokr/leo-git-statistics/commit/693c997618921808810e8848625ad561a10de87d))


### Bug Fixes

* add parent directory to Python path for module imports ([08f6ea1](https://github.com/leonardokr/leo-git-statistics/commit/08f6ea1205d63288976592ee39681cc56c8ee5c6))
* pass username and access_token as constructor arguments to Environment ([0d3bd8a](https://github.com/leonardokr/leo-git-statistics/commit/0d3bd8a0d303a76cc73174d4a37f7131d33c850e))
* remove /api/v1 prefix from route decorators ([0a04dec](https://github.com/leonardokr/leo-git-statistics/commit/0a04dec93b2dc5c7ea2f664a41e3cf6132da61f3))

## [1.0.1](https://github.com/leonardokr/leo-git-statistics/compare/v1.0.0...v1.0.1) (2026-02-13)


### Bug Fixes

* **action:** remove setup-python cache path for reusable action context ([a545027](https://github.com/leonardokr/leo-git-statistics/commit/a545027aa94501f7529c8f88effea502985f1405))

## 1.0.0 (2026-02-13)


### Features

* a script to test the templates ([b22699f](https://github.com/leonardokr/leo-git-statistics/commit/b22699f6488c54a5d4c3ed15a92bf630198aec61))
* **action:** add full workflow inputs and document template-vs-action usage ([8a3db0f](https://github.com/leonardokr/leo-git-statistics/commit/8a3db0fc9d0b26184eb2738a0ff99246bd004596))
* add application entry point and orchestrator ([122d600](https://github.com/leonardokr/leo-git-statistics/commit/122d6009681bace18e7783247f14de3704ee9194))
* add optional output_name to SVG generators ([ce55d07](https://github.com/leonardokr/leo-git-statistics/commit/ce55d0795b348199f95bbcaf54c2f0c6e8b38249))
* **calendar:** add weekly commit calendar generator and SVG template ([d13207a](https://github.com/leonardokr/leo-git-statistics/commit/d13207a6d0754f1c0f0fa799f041620a3f8e8ee1))
* **config:** add LANGUAGES_PUZZLE_TEMPLATE constant ([c2a440f](https://github.com/leonardokr/leo-git-statistics/commit/c2a440f869b39a0aad7dc25e1649b830c3eefa1d))
* **config:** add streak battery template configuration ([7d8b808](https://github.com/leonardokr/leo-git-statistics/commit/7d8b808430714e4f7b1865dbc876b24279055420))
* **config:** add theme selection in config.yml ([19b208b](https://github.com/leonardokr/leo-git-statistics/commit/19b208baa8331a7b625c4fdeff10b5f1df064293))
* **core:** add mock stats for testing without GitHub API ([a526937](https://github.com/leonardokr/leo-git-statistics/commit/a526937efe8c2bcba7e9004248c40ae6f15bbe17))
* **core:** collect weekly commit schedule data with privacy-safe metadata ([c297a0b](https://github.com/leonardokr/leo-git-statistics/commit/c297a0bf0a5c8fd9d834aec66f1978265ec90b77))
* **core:** implement core logic for config, environment, and stats collection ([674be46](https://github.com/leonardokr/leo-git-statistics/commit/674be465a72cb8e24bde3362a3575c9539d1a41c))
* **db:** add database management logic and initial data ([22eafe0](https://github.com/leonardokr/leo-git-statistics/commit/22eafe07ea8a51487cebdd76fdf0a8375b827aac))
* **formatter:** add treemap algorithm and palette color generation ([495801e](https://github.com/leonardokr/leo-git-statistics/commit/495801e285787ac8a185d4b08088f7804dedefd8))
* **generators:** add LanguagesPuzzleGenerator class ([12d7552](https://github.com/leonardokr/leo-git-statistics/commit/12d7552309930e0ef496514d6708f0cc0fee3414))
* **generators:** add modular SVG generators for stats cards ([ea5da3f](https://github.com/leonardokr/leo-git-statistics/commit/ea5da3fa753fba0682a9502efdd0b96d95a83118))
* **generators:** export LanguagesPuzzleGenerator ([7f0616e](https://github.com/leonardokr/leo-git-statistics/commit/7f0616e775be96307dc04dcd3b563fcbe197b0a2))
* **orchestrator:** generate streak card for all themes ([36f51d1](https://github.com/leonardokr/leo-git-statistics/commit/36f51d190b3352c4ff16bf573d67af2db319544e))
* **orchestrator:** register LanguagesPuzzleGenerator ([2d4c669](https://github.com/leonardokr/leo-git-statistics/commit/2d4c669e8ec0f780e6399a57d3adfd8bc91e8ac4))
* **presentation:** implement svg templates and stats formatting ([7e2ae98](https://github.com/leonardokr/leo-git-statistics/commit/7e2ae9852a39ba357683b97aee11e420682f7494))
* **puzzle:** add hue_spread and gap parameters to generator ([6f8741c](https://github.com/leonardokr/leo-git-statistics/commit/6f8741c52bae379feffd2cce4d059d36518339bc))
* **puzzle:** improve color palette with golden angle distribution ([7dd1ca2](https://github.com/leonardokr/leo-git-statistics/commit/7dd1ca20dd9d0076c689d92bd9ede6cc4c18f799))
* **puzzle:** use sqrt scaling for balanced block sizes ([4bd740c](https://github.com/leonardokr/leo-git-statistics/commit/4bd740c7c0532b792988eb67710664557b5f0bce))
* **stats:** add recent_contributions property for streak battery ([b1830a8](https://github.com/leonardokr/leo-git-statistics/commit/b1830a84c5d72e7a1803fdf7d634a6e7307541e2))
* **stats:** add streak calculation properties ([b695916](https://github.com/leonardokr/leo-git-statistics/commit/b69591670f4a5942400c9e905861e3123a83d347))
* support custom output filename via output_name ([1ca9550](https://github.com/leonardokr/leo-git-statistics/commit/1ca95506cee2f4f7cac2f8f90f5df1cfc2c934ef))
* **templates:** add contribution streak card ([18afc41](https://github.com/leonardokr/leo-git-statistics/commit/18afc410eb3ae51bcb3909b34f9ca1a4cb798947))
* **templates:** add languages_puzzle.svg treemap template ([6ec6ec9](https://github.com/leonardokr/leo-git-statistics/commit/6ec6ec9088e7639c0c5183a75abd91d12866ed72))
* **templates:** add streak battery SVG template ([5b52c0b](https://github.com/leonardokr/leo-git-statistics/commit/5b52c0be449150cecad446101b5e1d9b9be96b16))
* **templates:** redesign languages card with gradient bar ([6f11556](https://github.com/leonardokr/leo-git-statistics/commit/6f1155655b1d2a36db3e122614c1deae4870a54b))
* **templates:** redesign overview card with modern layout ([ce5416b](https://github.com/leonardokr/leo-git-statistics/commit/ce5416bc85b7221c1ef99cfb9da099fdaa02eb0f))
* **templates:** unify streak_battery visual style with gradient footer ([8d1a32a](https://github.com/leonardokr/leo-git-statistics/commit/8d1a32a7100c1776ed0b6a8214d4b96da7fd102e))
* **test:** add LanguagesPuzzleGenerator to generate_test ([2ee76d3](https://github.com/leonardokr/leo-git-statistics/commit/2ee76d3d1c55cd3a5c938876efa237b44815019d))
* **themes:** add commit calendar theme tokens across all theme packs ([b5b4298](https://github.com/leonardokr/leo-git-statistics/commit/b5b4298c4fe077df9ab975b1723a80d8be1564e7))
* **themes:** add default puzzle colors to theme loader ([3e162c3](https://github.com/leonardokr/leo-git-statistics/commit/3e162c3e3c83b6cf019b16ae64d443bd246bb64e))
* **themes:** add extensible theme system with YAML loader ([620a828](https://github.com/leonardokr/leo-git-statistics/commit/620a82803eedda619974d017f11075ec8237271f))
* **themes:** add puzzle_hue and color ranges for all themes ([9a9f835](https://github.com/leonardokr/leo-git-statistics/commit/9a9f835cf82a919e5420e077cb14e81465fe6dd9))
* **themes:** add puzzle_hue_spread to all themes for better color variety ([421d470](https://github.com/leonardokr/leo-git-statistics/commit/421d4702b9785cae421f13b8199a810519a9c33b))
* **utils:** add file system utility functions ([f3188ab](https://github.com/leonardokr/leo-git-statistics/commit/f3188abc4951e77b5ff7cabc0f2657e827a6f1f4))


### Bug Fixes

* add error handling for database file operations ([8fe6883](https://github.com/leonardokr/leo-git-statistics/commit/8fe688327f7258b3315faa35a06f9653c34f5280))
* add safe list coercion for REST API responses in StatsCollector ([bd4f0df](https://github.com/leonardokr/leo-git-statistics/commit/bd4f0df7dc30f69b12c3aa7aa78bbf037028fefd))
* adjust battery fill height in streak_battery template ([9740be1](https://github.com/leonardokr/leo-git-statistics/commit/9740be1741480bb4c34a6ea1e424565989210c2c))
* **calendar:** snap commit blocks to time buckets for consistent alignment ([fec33a6](https://github.com/leonardokr/leo-git-statistics/commit/fec33a6ffafbb8ce3bc59e95aa44cbdf5fbaf550))
* change time bucket minutes to 2 ([b1fbb18](https://github.com/leonardokr/leo-git-statistics/commit/b1fbb186170817f4cb119001ddb0810c73614d9f))
* **ci:** add write permissions and update actions versions ([28aaf19](https://github.com/leonardokr/leo-git-statistics/commit/28aaf1907898c1db344149489e41525769c02703))
* **ci:** correct python heredoc syntax in workflow ([aea2fb4](https://github.com/leonardokr/leo-git-statistics/commit/aea2fb4fe6fbe17473ddb8402fdbd363a9d13d37))
* **ci:** move git pull --rebase after commit to avoid push rejection ([55d2941](https://github.com/leonardokr/leo-git-statistics/commit/55d29413ece51a0ac66249a5c58827ba8a060939))
* correct dark mode colors in languages SVG ([8af90fd](https://github.com/leonardokr/leo-git-statistics/commit/8af90fdf0612baae1dc99be3b5091fd0a9609892))
* correct public repo exclusion logic in is_repo_type_excluded ([793fd78](https://github.com/leonardokr/leo-git-statistics/commit/793fd7843d2714cf383c1ed61d580a60b93ef042))
* disable recently-used languages to fix metrics error ([4688708](https://github.com/leonardokr/leo-git-statistics/commit/4688708081ae8a7abdfd9f631c6b7cd311e2804b))
* fixed radius on commit_calendar ([aa6e4d7](https://github.com/leonardokr/leo-git-statistics/commit/aa6e4d74b343620b1b2f136742d00eb9cde5d525))
* handle None repo_name in is_repo_name_invalid ([c544ddc](https://github.com/leonardokr/leo-git-statistics/commit/c544ddc10ea45bc4537dbd17f0bca151fbc2d276))
* **orchestrator:** pre-fetch stats to avoid race conditions in parallel generators ([a05db8c](https://github.com/leonardokr/leo-git-statistics/commit/a05db8cceff92b1270d4afbdbdc47674ce679faf))
* **puzzle:** update treemap dimensions to fit new card layout ([bb56475](https://github.com/leonardokr/leo-git-statistics/commit/bb56475807b9945b0cf0d777cc78cf286e19674c))
* remove direct os.environ modification in TrafficStats ([75fefe8](https://github.com/leonardokr/leo-git-statistics/commit/75fefe8c7cd1ca2185d36a28649658a315540ea7))
* replace bare except with specific exceptions in github_client ([325102e](https://github.com/leonardokr/leo-git-statistics/commit/325102e7f71f5ff9eda1b18af79b3b79c5bdb1fa))
* replace generic Exception catches with specific exceptions in GitHubClient ([41fabd4](https://github.com/leonardokr/leo-git-statistics/commit/41fabd4283bbd898fae58b1d08a0ad02e4e0bcc9))
* simplify streak_battery template layout ([ef8b13b](https://github.com/leonardokr/leo-git-statistics/commit/ef8b13baf16597119a1426e03f3d2c6fc1f5b162))
* standardize languages.svg dimensions to 495x195 ([41ade09](https://github.com/leonardokr/leo-git-statistics/commit/41ade097a6f32276ad44daffc0ca51efb12fd5cc))
* **stats:** filter contribution calendar to exclude future dates ([fdf2c95](https://github.com/leonardokr/leo-git-statistics/commit/fdf2c952dfd8cd727d5a7459fce09ea0f82258ce))
* **stats:** fixed templates animations ([fb704fc](https://github.com/leonardokr/leo-git-statistics/commit/fb704fcd934ac9b585fca98c42dbbbe90aaf8e93))
* **templates:** adjust streak informations positions ([b730393](https://github.com/leonardokr/leo-git-statistics/commit/b730393f16e1b4f99ac7181a557f9aa3df060cab))
* update tests to match current attribute paths and theme suffixes ([f8b1522](https://github.com/leonardokr/leo-git-statistics/commit/f8b1522aa7298df2f8b898fee0c598fe0908fb2b))
* use Path(__file__) for database path resolution ([8b958ce](https://github.com/leonardokr/leo-git-statistics/commit/8b958ce6807b8d9a926e04ac7b8ac1372d0d64de))
* **workflow:** remove deprecated output_action option from metrics ([6315ab9](https://github.com/leonardokr/leo-git-statistics/commit/6315ab9f51d5f568e8e1ecfc64b6b25d1d41ff30))
