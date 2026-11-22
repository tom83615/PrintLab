# Language policy and coverage

PrintLab provides a [Traditional Chinese introduction](../README.zh-TW.md) and an [English guide](../README.en.md). The default `README.md` and Chinese text maintained by PrintLab use Traditional Chinese. When both video platforms are available, YouTube is the primary link and Bilibili is the alternative. The current walkthrough has Chinese audio.

## What is in English

The English README and contribution and issue-reporting entry points give contributors and agents a shared starting point. Agents should communicate with users in the user's preferred language and retain the user's original statements as evidence.

There is no project-specific comparison showing that translating instructions alone improves an agent's reasoning. The reason for this choice is accessible onboarding and consistent maintenance for an international audience.

## What remains in Chinese

The workbench UI, generated messages, role prompts, detailed device and integration guides, and project templates include Traditional Chinese. Agents can read these references and explain them in the user's language.

Chinese Bambu Studio button names, accessibility/OCR match strings and fixtures represent the actual supported Chinese UI. Translating those literals would change device-control behavior. User projects, preferences, quotations, filenames and historical records also retain their original language. Unicode test cases continue to test non-English text and paths.

## How to continue the migration

- Write new or materially revised canonical technical documentation, identifiers and explanatory code comments in English. Keep the English and Chinese README aligned on capabilities, installation and limits.
- Translate detailed maintained references as they are revised, preserving commands, paths, schema keys, units, permissions and verification boundaries. Keep old public links working.
- Keep workbench copy in Traditional Chinese and preserve stable machine-readable values. Verify text changes against the screens and workflows that use them.
- Never rewrite a user's existing workspace or historical evidence merely to change its language.
