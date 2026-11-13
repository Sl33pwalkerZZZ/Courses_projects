# AI Integrations

**Verified:** 2026-11-09 source scan described in the technical audit. This document separates platform runtime integrations from AI technologies taught in course materials.

## Platform runtime

**No generative-AI inference provider was found in the bounded application scan** of `config/`, Django apps and `frontend/src/`. The audit found no OpenAI, Gemini, Anthropic/Claude, Groq, LangChain/LangGraph, embeddings, vector database, RAG service, agent orchestration or local LLM client in the learner request path. This is a scoped repository finding, not a claim that no uninspected external system exists.

The app uses ordinary Django REST APIs, JWT and deterministic server-side validation/grading for platform features. Do not describe course material about prompts, n8n, local LLMs or generative media as an AI integration in the product.

## Course-production TTS

- The Module 4 production workflow used the Silero `v5_cis_base_nostress` checkpoint and Russian `ru_roman` speaker. The project documents the MIT-licensed CIS base exception and includes the relevant `LICENSE_CIS` notice with approved deliverable provenance.
- The local helper source is reported as `course_assets/module_4/voice_candidates/prepare_roman_module4.py`; Module 4 source assets and canonical manifests identify the final narration and processing methods. Production generation is an offline asset workflow, not a deployed service.
- PyTorch/model cache and the isolated evaluation environment were local, not application dependencies or tracked production requirements. Reproduction may need separately provisioned compatible Python/PyTorch/checkpoint assets; verify the provenance document before regeneration.
- Earlier ElevenLabs Free and eSpeak outputs are historical/legacy comparison assets, excluded from the approved Module 4 production manifest. Do not reintroduce them as active narration without content-owner approval.
- Lesson 12 noise simulation/filtering uses conventional DSP where documented; do not claim it is AI denoising.

## AI technologies taught, not called by the platform

Course titles and import data cover language models, prompt engineering, research/knowledge workflows, n8n automation, document work, local LLMs, image generation, TTS/transcription and CapCut. The course source data and management commands author this curriculum. They do not establish app-side model API calls.

## Unknowns

- No complete audit of every local model cache, untracked generation script, external integration or production environment was performed.
- No inference provider credentials or secrets were read. Do not inspect or disclose them for routine documentation updates.
- Future AI integrations require an explicit architecture, data-handling, security and licensing review, with provider/model configuration documented separately from lessons that teach those tools.

Evidence: [technical inventory, AI section](../project-audit/01-technical-inventory.md#e-ai-and-intelligent-feature-inventory), [media audit, audio/TTS and licensing](../project-audit/03-media-and-production-audit.md#c-audio-tts-and-subtitle-production).
