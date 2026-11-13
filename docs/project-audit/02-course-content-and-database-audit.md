# AI Courses — Course Content and Database Audit

**Audit date:** 2026-11-09
**Branch:** `design/amethyst-motion` (four local commits ahead of `origin/design/amethyst-motion`)
**Scope:** Read-only audit of educational course/module/lesson metadata, assessment configuration, course import sources, media manifests and static frontend connections. This is not a learner-record audit or a browser runtime test.

Evidence labels: **CONFIRMED** = directly verified in the local read-only database or inspected source; **INFERRED** = supported by project conventions but not directly exercised; **UNKNOWN** = not present in inspected evidence or not verified.

## A. Snapshot and safety

**CONFIRMED:** The configured local SQLite database was opened using SQLite URI `mode=ro`, with `PRAGMA query_only=ON`. `PRAGMA integrity_check` returned `ok`; `PRAGMA foreign_key_check` returned no violations. No migrations, import commands, tests, writes, learner queries, attempts, submissions, answer choices, credentials, backups or production services were used. Course/module/lesson, quiz metadata/counts, assignments, certificate policy, image/attachment metadata and migration names/status were inspected. Quiz question/choice content and answer keys were not read. The private quiz-import JSON was not opened.

**CONFIRMED:** Current inventory is **10 courses, 38 modules and 114 lessons**. One course is published: Course 8. Courses 1–7 and 9–10 are unpublished in this database snapshot. Course 10 is unpublished.

## B. Complete course inventory

| ID | Course / slug | Status, level, enrollment | Modules / lessons | Learning metadata | Images / attachments | Assessment / certificate configuration | Source relationship |
|---:|---|---|---:|---|---:|---|---|
| 1 | **Test_Course** / `test_course` | unpublished; beginner; approval | 0 / 0 | 0/0 lessons have `LessonLearningContent` | 0 / 0 | none; none; none | No canonical source located in inspected course sources (origin unknown). |
| 2 | **AI Fundamentals for Work & Study** / `ai-fundamentals-work-study` | unpublished; beginner; approval | 5 / 15 | 0/15 lessons have `LessonLearningContent` | 0 / 0 | quiz 2 published (15 Q/60 choices, 70%, lesson 15); none; none | `courses/management/demo_course_data.py`; seeded by `seed_demo_courses`. |
| 3 | **Prompt Engineering for LLMs** / `prompt-engineering-llms` | unpublished; beginner; approval | 5 / 15 | 0/15 lessons have `LessonLearningContent` | 0 / 0 | none; none; none | `courses/management/demo_course_data.py`; seeded by `seed_demo_courses`. |
| 4 | **AI Research & Knowledge Systems** / `ai-research-knowledge-systems` | unpublished; intermediate; approval | 5 / 15 | 0/15 lessons have `LessonLearningContent` | 0 / 0 | none; none; none | `courses/management/demo_course_data.py`; seeded by `seed_demo_courses`. |
| 5 | **AI Automation with n8n** / `ai-automation-n8n` | unpublished; intermediate; approval | 5 / 15 | 0/15 lessons have `LessonLearningContent` | 0 / 0 | none; none; none | `courses/management/demo_course_data.py`; seeded by `seed_demo_courses`. |
| 6 | **AI for Documents & Office Work** / `ai-documents-office-work` | unpublished; intermediate; approval | 5 / 15 | 0/15 lessons have `LessonLearningContent` | 0 / 0 | none; none; none | `courses/management/demo_course_data.py`; seeded by `seed_demo_courses`. |
| 7 | **Local LLMs & Private AI** / `local-llms-private-ai` | unpublished; advanced; approval | 5 / 15 | 0/15 lessons have `LessonLearningContent` | 0 / 0 | quiz 1 published (2 Q/8 choices, 70%, lesson 88); none; none | `courses/management/demo_course_data.py`; seeded by `seed_demo_courses`. |
| 8 | **Как выбрать нейросеть под свою задачу** / `kak-vybrat-neyroset-pod-svoyu-zadachu` | published; beginner; approval | 1 / 6 | 6/6 lessons have `LessonLearningContent` | 0 / 0 | quiz 3 published (15 Q/60 choices, 70%, lesson 96); assignment 1 (text, lesson 96); policy enabled, issuer approved | `courses/management/first-course-content.json` + `course_sources/Глава_1_Выбор_ИИ_модели_и_сервиса.docx`; course import receipt. |
| 9 | **123** / `123` | unpublished; beginner; open | 2 / 3 | 0/3 lessons have `LessonLearningContent` | 0 / 0 | quiz 4 draft (1 Q/2 choices, 70%, lesson 97); none; none | No canonical course source located; test-looking content (origin unknown). |
| 10 | **ИИ для создания медиаконтента: от идеи до публикации** / `ai-media-content` | unpublished; beginner; open | 5 / 15 | 15/15 lessons have `LessonLearningContent` | 7 / 14 | none; none; none | CourseImport receipt + `course_sources/media_module_1.docx`; Modules 2–5 JSON sources. |

### Course descriptions and metadata

| Course | Category/direction | Description (database value) |
|---|---|---|
| 1 — Test_Course | TestCourse | TestCourse |
| 2 — AI Fundamentals for Work & Study | AI Foundations | Explore modern AI and language models through everyday study and work tasks. This course is for students and professionals who want a practical starting point. You will learn to frame useful requests, check responses, and build a small workflow that keeps human judgment in the loop. |
| 3 — Prompt Engineering for LLMs | AI Foundations | Learn to write, test, and maintain clear instructions for language models. This beginner course is for students and professionals who want more consistent results from AI assistants. You will finish with a small prompt library, example inputs, and a practical evaluation checklist. |
| 4 — AI Research & Knowledge Systems | Knowledge Systems | Explore how AI can support research without losing the connection between claims and sources. The course is for learners who already use AI assistants and want to organize research for personal or team projects. You will build a small knowledge workspace with source records, evidence notes, and a reviewable research brief. |
| 5 — AI Automation with n8n | Automation | Learn to design small automations that connect data, applications, and language models using n8n. This course suits learners comfortable with AI assistants who want to understand repeatable workflows. You will plan and test an automation with explicit inputs, validation, error handling, and a human approval step. |
| 6 — AI for Documents & Office Work | Productivity | Practice using language models to summarize, extract information from, and draft everyday office documents. The course is for learners who already use AI assistants and want a more dependable document process. You will create a reviewable workflow that preserves source facts, marks missing information, and produces a clear final handover. |
| 7 — Local LLMs & Private AI | Private AI | Explore the practical trade-offs of running language models under local control. This advanced course is for learners familiar with AI workflows who want to evaluate privacy, hardware, and operational constraints. You will design a small local knowledge workflow with a documented data boundary, model evaluation, and a recovery plan. |
| 8 — Как выбрать нейросеть под свою задачу | AI Foundations | Первая глава курса: основы искусственного интеллекта, принципы работы LLM, различия моделей и сервисов, методика сравнения инструментов и практическая карта выбора. Учебный материал на русском языке. Это только глава 1; следующее занятие об ИИ-агенте ещё не добавлено. |
| 9 — 123 | TestCourse | 123 |
| 10 — ИИ для создания медиаконтента: от идеи до публикации | AI Foundations | Результат модуля: слушатель выбирает безопасную и реалистичную идею медиапроекта, формулирует бриф, составляет запрос к ИИ, критически оценивает ответ и заполняет паспорт будущего ролика. Ориентир по времени: 3 занятия по 35–50 минут и 40–60 минут самостоятельной практики. Время зависит от подготовки слушателя. |

**CONFIRMED:** Course 10 description is still framed as a one-module/three-lesson result, although its current database inventory is five modules and 15 lessons. It should be reviewed before publication. This audit does not edit it. Course 1 and Course 9 contain sparse, test-looking titles/descriptions; their origin is **UNKNOWN**, so no cleanup is proposed without owner confirmation.

## C. Complete module and lesson inventory

The database schema has no separate module or lesson description fields: `courses_module` stores title/order/course, and `courses_lesson` stores title/order/`text_content`. For lesson descriptions below, the excerpt is the opening of the stored educational text. Full text remains in the database and canonical source files; it is intentionally not duplicated here. Objective strings are included for structured lessons. Learner data and assessment answers are excluded.

### Course 1 — Test_Course

**CONFIRMED:** No modules or lessons.

### Course 2 — AI Fundamentals for Work & Study

#### Module 1: Understanding Modern AI (database ID 1)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 1 | What AI can help you do | 671 chars; AI tools can help classify information, draft text, and suggest patterns. Their value depends on the task and the quality of the material you supply. Start with a bounde… | — | 0: — | no graded relation; no media |
| 2 / 2 | Language models and their limits | 710 chars; A language model generates text from patterns learned during training and the context available in a request. Fluent wording alone does not establish that an answer is t… | — | 0: — | no graded relation; no media |
| 3 / 3 | Choosing a task and defining success | 672 chars; A vague goal makes an AI result difficult to judge. Define the audience, expected output, and the conditions that would make the result useful. Use a small acceptance ch… | — | 0: — | no graded relation; no media |

#### Module 2: Working with AI Assistants (database ID 2)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 4 | Giving an assistant a clear brief | 703 chars; An assistant needs enough context to understand your request. Explain the situation and identify the exact deliverable instead of relying on a broad instruction. Provide… | — | 0: — | no graded relation; no media |
| 2 / 5 | Using follow-up questions | 674 chars; An AI conversation can develop a result in stages. Follow-up questions work best when they refer to a concrete part of the previous response. Ask for a correction, compa… | — | 0: — | no graded relation; no media |
| 3 / 6 | Keeping reusable working notes | 682 chars; Useful AI interactions can become reusable notes. Save the request, essential context, and your review criteria rather than relying on an unstructured chat history. Remo… | — | 0: — | no graded relation; no media |

#### Module 3: Prompting Fundamentals (database ID 3)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 7 | Instructions, context, and output format | 693 chars; A prompt combines a task with the material and rules needed to carry it out. Keeping these parts separate helps you spot missing information. Name the action explicitly,… | — | 0: — | no graded relation; no media |
| 2 / 8 | Examples and useful constraints | 740 chars; An example can communicate style or structure more clearly than an adjective. Constraints define what the assistant should preserve, exclude, or leave unresolved. Choose… | — | 0: — | no graded relation; no media |
| 3 / 9 | Improving a prompt through comparison | 643 chars; Prompt improvement is a small experiment. Compare versions on the same task so you can identify which change made a difference. Change one important instruction at a tim… | — | 0: — | no graded relation; no media |

#### Module 4: Responsible and Reliable AI Use (database ID 4)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 10 | Checking claims and references | 700 chars; Generated claims need verification when they influence a decision or appear in published work. A plausible reference is not enough; inspect the original source. Separate… | — | 0: — | no graded relation; no media |
| 2 / 11 | Protecting personal and confidential information | 689 chars; Task context can contain personal or confidential information. Decide what a tool may receive before pasting material into it. Follow the rules that apply to your organi… | — | 0: — | no graded relation; no media |
| 3 / 12 | Reviewing bias and communicating AI assistance | 739 chars; An AI draft may make assumptions about people or circumstances that the source material does not support. Review both its factual claims and its framing. Look for stereo… | — | 0: — | no graded relation; no media |

#### Module 5: Practical AI Workflow (database ID 5)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 13 | Mapping a small human-in-the-loop workflow | 714 chars; A workflow connects several actions toward a repeatable result. Begin with a simple sequence that makes the input, AI step, and human review visible. Identify who suppli… | — | 0: — | no graded relation; no media |
| 2 / 14 | Measuring usefulness and keeping a log | 670 chars; A workflow is useful when it improves the actual task, not merely when it produces text quickly. Measure the effort of preparing, reviewing, and correcting the result. R… | — | 0: — | no graded relation; no media |
| 3 / 15 | Presenting your practical AI workflow | 693 chars; A final workflow should be understandable to someone who did not build it. Describe its purpose, required inputs, sequence, and limits in a short handover note. Include … | — | 0: — | quiz 2 published 70%; no media |

### Course 3 — Prompt Engineering for LLMs

#### Module 1: How LLMs Interpret Instructions (database ID 6)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 16 | Instructions and supplied material | 797 chars; A prompt combines instructions with information the model should work on. Make the distinction visible so a reader can identify the task without guessing. Put the task b… | — | 0: — | no graded relation; no media |
| 2 / 17 | Context and uncertainty | 716 chars; A model can only use the context available to it and its learned patterns. It may fill a missing detail with a plausible statement unless the task defines another respon… | — | 0: — | no graded relation; no media |
| 3 / 18 | Why similar prompts can produce different answers | 677 chars; Language model output can vary even when a task looks unchanged. A single impressive answer is weak evidence that a prompt will work repeatedly. Small changes in wording… | — | 0: — | no graded relation; no media |

#### Module 2: Anatomy of a Strong Prompt (database ID 7)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 19 | Writing a specific task statement | 685 chars; Start by stating the action and its intended result. Broad requests such as 'improve this' leave the model to choose both the problem and the success criteria. Describe … | — | 0: — | no graded relation; no media |
| 2 / 20 | Adding the right context | 743 chars; Context explains the situation in which an answer will be used. Include the audience, purpose, and relevant source facts without burying the task in unrelated history. S… | — | 0: — | no graded relation; no media |
| 3 / 21 | Defining the output contract | 670 chars; The output contract describes the shape and boundaries of a response. It can specify headings, fields, length, and how empty values should be represented. Choose a forma… | — | 0: — | no graded relation; no media |

#### Module 3: Context, Examples and Constraints (database ID 8)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 22 | Showing examples without overfitting | 718 chars; Examples demonstrate the relationship between an input and a desired output. They are most useful when they explain a pattern rather than merely supply an answer to copy… | — | 0: — | no graded relation; no media |
| 2 / 23 | Constraints and conflicting requirements | 735 chars; Constraints define limits such as length, tone, or prohibited assumptions. Too many competing requirements can make a prompt hard to satisfy or evaluate. Rank essential … | — | 0: — | no graded relation; no media |
| 3 / 24 | Preparing long source material | 731 chars; Long inputs are easier to work with when their sections and purpose are clear. Preserve structure so important facts can be traced back to the original material. Split m… | — | 0: — | no graded relation; no media |

#### Module 4: Iteration and Evaluation (database ID 9)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 25 | Creating a small test set | 693 chars; A test set is a collection of inputs that reveals how a prompt behaves. Include ordinary cases, missing information, and a case that should be rejected or sent for revie… | — | 0: — | no graded relation; no media |
| 2 / 26 | Comparing one change at a time | 673 chars; Iteration should help you learn why a result changed. Revising the task, examples, and output format together makes that explanation difficult. Change one major element,… | — | 0: — | no graded relation; no media |
| 3 / 27 | Scoring accuracy and usability | 689 chars; A response can be fluent yet unusable for the task. Evaluate correctness, completeness, source support, and whether the output fits its intended workflow. Use a short ru… | — | 0: — | no graded relation; no media |

#### Module 5: Building a Prompt Library (database ID 10)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 28 | Turning a prompt into a template | 686 chars; A reusable prompt separates stable instructions from values that change for each task. Clearly named placeholders make the expected inputs easier to supply. Document req… | — | 0: — | no graded relation; no media |
| 2 / 29 | Documenting versions and limitations | 674 chars; A prompt library needs enough context for someone else to use it responsibly. Store the purpose, input requirements, tested cases, and known limitations beside each temp… | — | 0: — | no graded relation; no media |
| 3 / 30 | Delivering your starter prompt library | 717 chars; A starter library should solve a few clearly defined tasks well. A small collection with tests is easier to maintain than many unverified prompts. Choose complementary t… | — | 0: — | no graded relation; no media |

### Course 4 — AI Research & Knowledge Systems

#### Module 1: From Information to Knowledge (database ID 11)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 31 | Defining a research question | 711 chars; A research question gives direction to the material you collect. It should be narrow enough to answer and connected to a decision or learning goal. Describe the scope, i… | — | 0: — | no graded relation; no media |
| 2 / 32 | Distinguishing facts, interpretations, and gaps | 685 chars; Research notes often mix reported facts with a reader's interpretation. Keeping them separate prevents a tentative idea from becoming an unsupported conclusion. Label di… | — | 0: — | no graded relation; no media |
| 3 / 33 | Designing a source record | 637 chars; A source record stores enough information to find and assess a document later. A saved link alone rarely explains why a source was useful. Record its title, author or or… | — | 0: — | no graded relation; no media |

#### Module 2: AI-Assisted Research (database ID 12)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 34 | Planning a research search | 701 chars; Use an AI assistant to suggest search terms and possible angles before collecting evidence. Suggestions are a starting plan rather than proof that useful sources exist. … | — | 0: — | no graded relation; no media |
| 2 / 35 | Summarizing a supplied source | 697 chars; A source-grounded summary should reflect the supplied document, including its limits. It should not blend in outside facts unless the task explicitly asks for separate b… | — | 0: — | no graded relation; no media |
| 3 / 36 | Comparing several sources | 704 chars; Comparison reveals agreement, disagreement, and differences in scope. Sources can appear to conflict because they study different groups or use different definitions. Cr… | — | 0: — | no graded relation; no media |

#### Module 3: Working with Sources (database ID 13)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 37 | Checking credibility and relevance | 722 chars; A source can be authentic and still be unsuitable for your question. Assess its origin, evidence, incentives, and relationship to the claim you need to evaluate. Prefer … | — | 0: — | no graded relation; no media |
| 2 / 38 | Keeping citations connected to claims | 669 chars; A citation is useful when a reader can locate evidence for the associated statement. A valid link does not guarantee that the linked document supports the claim. Store c… | — | 0: — | no graded relation; no media |
| 3 / 39 | Handling disagreement and missing evidence | 709 chars; Conflicting evidence is a research result worth preserving. Do not ask an assistant to force agreement merely to make the final brief sound decisive. Record the disagree… | — | 0: — | no graded relation; no media |

#### Module 4: Building a Knowledge Base (database ID 14)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 40 | Choosing a simple information structure | 666 chars; A knowledge base is a system for finding and reusing verified material. Start with a small structure that matches how you expect to ask questions later. Separate source … | — | 0: — | no graded relation; no media |
| 2 / 41 | Adding tags and useful connections | 669 chars; Tags describe shared themes, while links express a specific relationship between notes. Use both sparingly so they support navigation instead of adding maintenance work.… | — | 0: — | no graded relation; no media |
| 3 / 42 | Maintaining a current knowledge base | 637 chars; Knowledge becomes less reliable when old material looks current. Store review dates and identify which notes depend on changing facts or policies. Assign ownership where… | — | 0: — | no graded relation; no media |

#### Module 5: Final Research Workspace (database ID 15)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 43 | Assembling a small evidence collection | 663 chars; The final workspace should demonstrate a complete path from question to evidence. Choose a manageable collection that you can inspect rather than maximizing the number o… | — | 0: — | no graded relation; no media |
| 2 / 44 | Writing an evidence-based brief | 719 chars; A research brief explains what the evidence supports and what remains uncertain. Its structure should help the intended reader make a decision or choose a next step. Sta… | — | 0: — | no graded relation; no media |
| 3 / 45 | Reviewing and handing over the workspace | 715 chars; A workspace is ready to share when another person can navigate it and verify its conclusions. A handover should explain the structure and the remaining work. Ask a revie… | — | 0: — | no graded relation; no media |

### Course 5 — AI Automation with n8n

#### Module 1: Automation Fundamentals (database ID 16)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 46 | Why automate repetitive work? | 750 chars; Automation is useful when a recurring task has understandable inputs and a consistent process. Begin with work whose successful result you can describe and check. Estima… | — | 0: — | no graded relation; no media |
| 2 / 47 | Mapping a workflow | 686 chars; A workflow map describes the route from an incoming event to a useful result. Include decision points and exceptions before choosing particular tools. Label the data nee… | — | 0: — | no graded relation; no media |
| 3 / 48 | Triggers, actions, and data flow | 667 chars; A trigger starts a workflow, while later actions transform data or interact with another system. Data flow determines which values are available to each action. Define a… | — | 0: — | no graded relation; no media |

#### Module 2: Working with n8n (database ID 17)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 49 | Building a small node sequence | 671 chars; In n8n, a workflow connects nodes that perform steps on data. Start with a manual trigger and a few transformations so you can inspect the process safely. Give nodes nam… | — | 0: — | no graded relation; no media |
| 2 / 50 | Mapping fields with expressions | 678 chars; Expressions let a node use values from workflow data rather than fixed text. Field mapping translates an incoming record into the structure the next step expects. Check … | — | 0: — | no graded relation; no media |
| 3 / 51 | Credentials and safe practice runs | 709 chars; Connected applications often require credentials. Keep credentials separate from workflow examples and use limited-access test resources while learning. Inspect a workfl… | — | 0: — | no graded relation; no media |

#### Module 3: Adding LLMs to Workflows (database ID 18)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 52 | Choosing the model's responsibility | 718 chars; An LLM step should have a narrow responsibility with a checkable result. Use ordinary workflow logic for exact rules and let the model handle language tasks that need in… | — | 0: — | no graded relation; no media |
| 2 / 53 | Requesting and validating structured output | 711 chars; Structured output helps later workflow steps consume a model response. Asking for fields is only the first step; the returned data still needs validation. Check parsing,… | — | 0: — | no graded relation; no media |
| 3 / 54 | Keeping source data distinct from instructions | 746 chars; Incoming messages may contain text that tries to redirect an AI step. Treat imported material as evidence to analyze rather than authority over the workflow. Label sourc… | — | 0: — | no graded relation; no media |

#### Module 4: Reliable AI Automations (database ID 19)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 55 | Handling failures and retries | 719 chars; External services can time out or reject a request. A reliable workflow distinguishes temporary failures from invalid data and records what happened. Limit retries and a… | — | 0: — | no graded relation; no media |
| 2 / 56 | Adding human approval | 723 chars; Human approval is useful where the workflow proposes an action that affects people or shared records. The reviewer needs enough information to judge the proposal. Show t… | — | 0: — | no graded relation; no media |
| 3 / 57 | Logging and measuring a workflow | 720 chars; Execution logs help explain where a workflow failed or became expensive. Record enough information to investigate without copying sensitive source material into every lo… | — | 0: — | no graded relation; no media |

#### Module 5: Final Automation Project (database ID 20)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 58 | Preparing the project specification | 691 chars; A project specification turns a workflow idea into a testable agreement. State the input, desired result, allowed actions, and conditions that require review. Keep the f… | — | 0: — | no graded relation; no media |
| 2 / 59 | Testing normal and exceptional inputs | 716 chars; Final testing should cover the workflow's entire path, including branches that do not produce a successful result. Failures are useful evidence of whether safeguards wor… | — | 0: — | no graded relation; no media |
| 3 / 60 | Documenting operation and recovery | 674 chars; A finished workflow needs an operating guide for someone returning after a break. Explain how to run a test, inspect results, stop actions, and recover from a failed ste… | — | 0: — | no graded relation; no media |

### Course 6 — AI for Documents & Office Work

#### Module 1: AI and Document Workflows (database ID 21)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 61 | Choosing a document task | 665 chars; Document work includes reading, extracting, drafting, and reviewing. Choose one of these tasks before asking an assistant to work on a file. Define the reader and the re… | — | 0: — | no graded relation; no media |
| 2 / 62 | Preparing source material | 713 chars; Documents may contain headings, tables, scanned text, or comments that affect interpretation. Check what the assistant actually receives before trusting its output. Pres… | — | 0: — | no graded relation; no media |
| 3 / 63 | Planning review and document versions | 704 chars; A document workflow needs a way to distinguish a source, an AI draft, and an approved version. Clear version labels reduce accidental use of unfinished work. Record the … | — | 0: — | no graded relation; no media |

#### Module 2: Summarization and Extraction (database ID 22)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 64 | Summarizing for a particular reader | 766 chars; A useful summary selects information according to the reader's purpose. It should preserve key facts and limitations rather than simply shorten every paragraph equally. … | — | 0: — | no graded relation; no media |
| 2 / 65 | Extracting fields and missing values | 687 chars; Extraction turns a document into a set of named fields. Decide what counts as evidence for each field and how to mark information that is not present. Keep dates, amount… | — | 0: — | no graded relation; no media |
| 3 / 66 | Comparing document versions | 714 chars; Version comparison asks what changed and why those changes matter. A generated comparison should be checked against both documents before it guides decisions. Separate a… | — | 0: — | no graded relation; no media |

#### Module 3: Drafting and Rewriting (database ID 23)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 67 | Drafting from an approved brief | 702 chars; An approved brief gives a drafting assistant a factual boundary. It should contain the message's purpose, audience, required facts, and any unanswered questions. Ask for… | — | 0: — | no graded relation; no media |
| 2 / 68 | Rewriting while preserving meaning | 724 chars; Rewriting can improve clarity, tone, or length without changing the underlying message. State which elements must remain exact and which may be rephrased. Compare the re… | — | 0: — | no graded relation; no media |
| 3 / 69 | Reviewing tone and accessibility | 707 chars; Office documents should be understandable to the people expected to act on them. Review tone, sentence structure, and unexplained terms with that audience in mind. Ask a… | — | 0: — | no graded relation; no media |

#### Module 4: Structured Office Workflows (database ID 24)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 70 | Creating reusable document templates | 718 chars; Templates make recurring documents easier to prepare and review. Separate fixed structure from fields that need fresh facts each time. Label required fields and provide … | — | 0: — | no graded relation; no media |
| 2 / 71 | From notes to action records | 737 chars; Action records connect a task to responsibility and timing. Meeting notes often leave one of these elements uncertain, so extraction needs a review step. Preserve the wo… | — | 0: — | no graded relation; no media |
| 3 / 72 | Quality checks before sharing | 653 chars; A final quality check should focus on errors that matter to the document's use. Include source accuracy, completeness, privacy, and clear ownership of approval. Use a sh… | — | 0: — | no graded relation; no media |

#### Module 5: Final Document Workflow (database ID 25)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 73 | Defining the final workflow | 610 chars; The final project should connect a source document to a reviewed deliverable. Choose a realistic but manageable office task with a clear audience. Specify the input form… | — | 0: — | no graded relation; no media |
| 2 / 74 | Testing the workflow against difficult inputs | 699 chars; Document workflows should cope with incomplete or inconsistent material. Test these cases before using a polished output as evidence that the process works. Include an i… | — | 0: — | no graded relation; no media |
| 3 / 75 | Delivering the document workflow guide | 672 chars; A handover guide explains how another person can repeat your process. Include accepted inputs, templates, review criteria, and where approved output is stored. Show one … | — | 0: — | no graded relation; no media |

### Course 7 — Local LLMs & Private AI

#### Module 1: Local AI Fundamentals (database ID 26)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 76 | What local inference means | 757 chars; Local inference means a model generates responses on hardware you control. It changes where computation happens, but it does not automatically settle every privacy quest… | — | 0: — | no graded relation; no media |
| 2 / 77 | Defining a privacy boundary | 682 chars; A privacy boundary states which data may enter the workflow and where it may be stored or transmitted. Write it before choosing tools or importing documents. Include doc… | — | 0: — | no graded relation; no media |
| 3 / 78 | Evaluating local and hosted trade-offs | 768 chars; Local and hosted systems distribute costs and responsibilities differently. Compare them against a defined task rather than assuming one option is universally better. Co… | — | 0: — | no graded relation; no media |

#### Module 2: Models and Hardware (database ID 27)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 79 | Choosing a model for the task | 706 chars; A model should be selected by how well it handles your workload, not by its name alone. Build a small evaluation set before downloading several large candidates. Check t… | — | 0: — | no graded relation; no media |
| 2 / 80 | Memory, context, and quantization | 762 chars; Local inference has practical memory limits. Model weights, runtime overhead, and the active context all contribute to resource use. Quantization can reduce the resource… | — | 0: — | no graded relation; no media |
| 3 / 81 | Measuring speed and useful quality | 693 chars; Speed matters only in relation to an acceptable result. Compare latency, completion quality, and review effort under consistent test conditions. Record hardware, model v… | — | 0: — | no graded relation; no media |

#### Module 3: Running a Local LLM (database ID 28)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 82 | Preparing a controlled runtime | 733 chars; A local runtime loads a model and exposes a way to send requests. Prepare a controlled experiment with trusted software and fictional inputs before adding integrations. … | — | 0: — | no graded relation; no media |
| 2 / 83 | Verifying local access and connections | 751 chars; A model server may expose an interface to other programs or devices. Check its listening address and access controls before treating it as a private local service. Keep … | — | 0: — | no graded relation; no media |
| 3 / 84 | Testing prompts and failure behavior | 714 chars; A running model still needs behavioral tests. Check whether it follows the task, uses supplied evidence, and handles an incomplete input without inventing facts. Also te… | — | 0: — | no graded relation; no media |

#### Module 4: Private Knowledge Workflows (database ID 29)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 85 | Preparing a local document collection | 769 chars; A local knowledge workflow starts with a deliberately selected document collection. Keep original sources and derived artifacts organized within the chosen privacy bound… | — | 0: — | no graded relation; no media |
| 2 / 86 | Retrieving evidence before generation | 751 chars; Retrieval selects relevant source material before a model answers a question. It can improve access to a document collection, but it does not guarantee that the answer i… | — | 0: — | no graded relation; no media |
| 3 / 87 | Reviewing answers, logs, and retention | 734 chars; A private knowledge workflow needs checks for both answer quality and stored data. A correct answer does not prove that the system's logs or backups respect the boundary… | — | 0: — | no graded relation; no media |

#### Module 5: Final Local AI Project (database ID 30)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 88 | Specifying a local knowledge assistant | 672 chars; The final project should demonstrate one useful task inside a documented local boundary. Choose a small collection and limit the assistant's responsibilities. Define the… | — | 0: — | quiz 1 published 70%; no media |
| 2 / 89 | Evaluating the complete local workflow | 673 chars; Evaluate the project from document input to reviewed answer. Include retrieval quality, source support, response time, and behavior when components fail. Use a fixed set… | — | 0: — | no graded relation; no media |
| 3 / 90 | Documenting maintenance and recovery | 755 chars; A local deployment needs a plan for updates, backups, and failure recovery. Its operating guide should make these responsibilities clear to a future maintainer. Record t… | — | 0: — | no graded relation; no media |

### Course 8 — Как выбрать нейросеть под свою задачу

#### Module 1: Модуль 1. Основы искусственного интеллекта и выбор ИИ-инструмента (database ID 31)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 91 | Что такое искусственный интеллект | 2584 chars; ГЛАВА 1 Что такое искусственный интеллект и как правильно выбрать ИИ-модель или сервис Учебно-методический материал для курса «Как выбрать нейросеть под свою задачу» Окт… | Объяснить связь между ИИ, машинным обучением, глубоким обучением и LLM.; Отличить генеративный ИИ от всей области искусственного интеллекта. | 1: — | no graded relation; no media |
| 2 / 92 | Как работают современные языковые модели | 1303 chars; 1.2. Как работает современная языковая модель Большая языковая модель (Large Language Model, LLM) обучается на больших объёмах текстовой и иной информации, обнаруживая з… | Проследить путь от запроса к ответу языковой модели.; Объяснить ограничения, галлюцинации и необходимость проверки. | 1: — | no graded relation; no media |
| 3 / 93 | Разница между ИИ-моделью и ИИ-сервисом | 862 chars; 1.3. Чем отличается ИИ-модель от ИИ-сервиса ИИ-модель — обученная нейронная сеть, непосредственно обрабатывающая запросы. ИИ-сервис — готовый продукт, обеспечивающий удо… | Различать обученную модель и сервис с интерфейсом и инструментами.; Объяснить, почему модель и сервис не связаны отношением «один к одному». | 1: — | no graded relation; no media |
| 4 / 94 | Виды нейросетей и обзор популярных сервисов | 1888 chars; 1.4. Виды нейросетей и области применения Категория \| Типовые задачи \| Примеры Текстовые языковые модели \| Документы, перевод, анализ требований, объяснения \| GPT, Claud… | Соотнести рабочую задачу с категорией ИИ-инструментов.; Сравнить назначение сервисов, учитывая изменяемость их функций. | 2: — | no graded relation; no media |
| 5 / 95 | Методика выбора ИИ-инструмента | 1840 chars; 1.6. Как правильно выбрать модель или сервис Шаг 1. Сформулировать задачу Вместо вопроса «Какая нейросеть лучше?» следует спросить: «Какой результат мне нужно получить и… | Применить пять шагов выбора ИИ-инструмента.; Сформулировать единые критерии и провести обезличенное сравнение. | 1: — | no graded relation; no media |
| 6 / 96 | Практическая работа: карта выбора ИИ | 2362 chars; 1.7. Практическая работа: выбор ИИ под собственную задачу Рекомендуемая продолжительность: 30–40 минут. Задание: выбрать реальную рабочую задачу, определить необходимые … | Составить карту выбора для своей рабочей задачи.; Обосновать решение по результатам сравнения и обозначить риски. | 2: — | assignment 1, quiz 3 published 70%; no media |

### Course 9 — 123

#### Module 1: 123 (database ID 32)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 97 | 123 | **EMPTY** (0 text characters) | — | 0: — | quiz 4 draft 70%; no media |
| 2 / 98 | 321 | **EMPTY** (0 text characters) | — | 0: — | no graded relation; no media |

#### Module 2: 123 (database ID 33)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 99 | 123 | **EMPTY** (0 text characters) | — | 0: — | no graded relation; no media |

### Course 10 — ИИ для создания медиаконтента: от идеи до публикации

#### Module 1: Основы ИИ в медиапроизводстве (database ID 34)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 100 | Как генеративный ИИ помогает создавать медиаконтент | 3384 chars; 1. От идеи к готовому материалу Представьте задачу: нужно рассказать о студенческом научном проекте в ролике на одну минуту. Недостаточно нажать кнопку «Сгенерировать ви… | Различать обычную автоматизацию и генеративный ИИ.; Называть этапы создания медиаконтента, где ИИ может помочь.; Определять задачи, в которых без человека нельзя принимать окончательное решение. | 6: — | no graded relation; no media |
| 2 / 101 | Бриф, промпт и выбор ИИ-инструмента | 3765 chars; 1. Почему сначала нужен бриф Нечёткая команда «Сделай интересное видео» обычно приводит к случайному результату. Даже хороший ИИ-инструмент не знает, кому предназначен м… | Составлять простой медиабриф перед работой с ИИ.; Писать конкретный запрос с ограничениями и форматом результата.; Сравнивать предложенный ИИ результат с исходной задачей. | 6: — | no graded relation; no media |
| 3 / 102 | Проверка фактов, права и прозрачность использования ИИ | 5480 chars; 1. Почему правдоподобного текста недостаточно ИИ способен составить связный и убедительный текст даже тогда, когда исходных сведений мало. Он может ошибиться в датах, пе… | Проверять фактические утверждения, предложенные ИИ.; Распознавать основные риски генеративного медиаконтента.; Указывать источники и роль ИИ в подготовке публикации. | 9: — | no graded relation; no media |

#### Module 2: Тексты и сценарии с помощью ИИ (database ID 35)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 103 | Поиск идей и подготовка медиабрифа | 8453 chars; 1. От темы к понятной идее В этом модуле мы превратим паспорт медиапроекта из первого модуля в рабочий бриф, сценарий и несколько версий публикации. Начинайте с уже выбр… | Отбирать идеи по интересу аудитории, цели и доступности проверяемых материалов.; Составлять медиабриф с темой, сообщением, площадкой, форматом, тоном и длительностью.; Использовать ИИ для поиска вариантов, не принимая предложения модели за факты. | 8: — | no graded relation; no media |
| 2 / 104 | Создание сценариев с помощью ИИ | 9216 chars; 1. Зачем сценарию нужна структура В предыдущем уроке мы определили, кому и что хотим объяснить. Теперь бриф нужно превратить в последовательность речи, кадров и переходо… | Строить сценарий ролика на 60–90 секунд с понятным началом, основной частью и завершением.; Уточнять запрос к ИИ и редактировать черновик по брифу, фактам и возможностям съёмки.; Разделять закадровый текст и визуальный ряд в простой раскадровке. | 9: — | no graded relation; no media |
| 3 / 105 | Адаптация медиаконтента для разных площадок | 9887 chars; 1. Одна история — несколько редакторских задач В предыдущем уроке получился сценарный черновик. Теперь из него нужно подготовить версии для разных ситуаций просмотра. Ад… | Различать задачи развёрнутого видео, короткого ролика и текстовой публикации.; Адаптировать начало, темп, заголовок и призыв к действию под аудиторию без изменения фактов.; Сравнивать версии одной истории и выявлять смысловые искажения после сокращения. | 9: — | no graded relation; no media |

#### Module 3: Создание изображений и графики с помощью ИИ (database ID 36)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 106 | Генерация изображений с помощью ИИ | 9024 chars; 1. Зачем медиапроекту изображение В предыдущем модуле мы подготовили бриф и сценарий. Теперь нужно определить, какие мысли действительно требуют графического пояснения. … | Составлять визуальный запрос с объектом, композицией, светом, стилем и соотношением сторон.; Сравнивать варианты изображения по медиабрифу, а не только по внешней привлекательности.; Распознавать ошибки генерации и отличать учебную иллюстрацию от документального свидетельства. | 9: — | no graded relation; 2 image(s) |
| 2 / 107 | Создание обложек, карточек и инфографики | 7919 chars; 1. От изображения к сообщению Изображение само по себе ещё не является обложкой или информационной карточкой. Нужно решить, что зритель увидит первым, что прочитает втор… | Строить визуальную иерархию обложки, социальной карточки и информационной схемы.; Сочетать условные изображения с проверенными заголовками и пояснениями.; Проверять читаемость, контраст и смысл графики, не добавляя вымышленных данных. | 9: — | no graded relation; 2 image(s) |
| 3 / 108 | Единый визуальный стиль медиапроекта | 9238 chars; 1. Зачем комплекту единый стиль В модуле уже появились идея иллюстрации, обложка и схема. Если каждый материал оформлять заново, зрителю трудно понять, что они относятся… | Фиксировать палитру, типографические роли и композиционные правила в кратком руководстве по стилю.; Проверять согласованность нескольких изображений без подмены их фактического смысла.; Готовить проверенные графические файлы и понятную структуру папок для работы в CapCut Desktop. | 9: — | no graded relation; 2 image(s) |

#### Module 4: Создание и обработка аудио с помощью ИИ (database ID 37)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 109 | Генерация речи и озвучка медиаматериалов | 9220 chars; 1. От сценария к звучащему тексту В модуле 2 мы подготовили сценарий, а в модуле 3 — визуальные материалы. Теперь нужно связать их с речью. Озвучка должна помогать понят… | Объяснять различие между синтезированной речью и записью человеческого диктора.; Готовить текст для звучания и проверять произношение, паузы, интонацию и темп.; Планировать озвучку с учётом согласия, происхождения голоса и редакторской проверки. | 9: — | no graded relation; 1 audio |
| 2 / 110 | Распознавание речи и создание субтитров | 8249 chars; 1. Почему автоматический текст нужно проверять Видеоматериал полезно сопровождать текстом: он помогает следить за речью, смотреть без звука и понимать содержание людям, … | Различать распознавание речи, расшифровку и перевод, сохраняя смысл источника.; Исправлять ошибки транскрипции и делить субтитры по смыслу и времени.; Читать структуру SRT и проверять доступность, синхронизацию и конфиденциальность материалов. | 9: — | no graded relation; 1 audio, 2 srt |
| 3 / 111 | Обработка звука и подготовка аудио для монтажа | 9686 chars; 1. Обработка начинается с прослушивания На этом этапе есть сценарий, план озвучки и субтитров. Обработка нужна, чтобы речь была понятной и согласованной с остальными эле… | Различать частоту дискретизации, каналы, уровень сигнала и клиппинг.; Оценивать разборчивость речи и сравнивать обработку с оригиналом без ложного улучшения громкостью.; Готовить проверенные аудиофайлы для монтажа с учётом формата, версий и происхождения. | 9: — | no graded relation; 1 image(s), 2 audio |

#### Module 5: Создание и монтаж видео в CapCut Desktop (database ID 39)

| Lesson order / ID | Title | Stored-text summary | Objectives | Sections | Practice, assessment and media |
|---|---|---|---|---:|---|
| 1 / 113 | Подготовка видеопроекта и организация материалов | 15327 chars; 1. От медиабрифа к монтажному плану В предыдущих модулях вы подготовили текст, изображения и звук. Теперь нужно собрать их в последовательность, которую зритель успеет п… | Преобразовывать медиабриф в кадровый план с понятной последовательностью изображения, речи и подписей.; Организовывать исходники и сведения о правах так, чтобы проект можно было безопасно открыть повторно.; Создавать проект в CapCut Desktop, импортировать материалы и проверять исходный формат кадра. | 9: — | no graded relation; 3 video |
| 2 / 114 | Монтаж, озвучка и интеллектуальные инструменты | 15270 chars; 1. От набора клипов к связному сообщению Монтаж — выбор и организация изображения и звука во времени. Он меняет не только длительность, но и смысл. Два кадра рядом могут… | Собирать понятную последовательность кадров и исправлять стыки с помощью обрезки и разделения клипов.; Согласовывать озвучку, изображение и читаемые подписи без перегрузки сообщения.; Проверять результаты интеллектуальных инструментов и заменять недоступные функции ручными действиями. | 9: — | no graded relation; 3 video, 2 vtt |
| 3 / 115 | Экспорт, адаптация и подготовка видео к публикации | 12931 chars; 1. Сохранение проекта и экспорт — разные задачи Сохранённый проект позволяет продолжить монтаж. Экспорт превращает выбранную последовательность в видеофайл для просмотра… | Выбирать параметры экспорта по задаче и различать размер кадра, частоту, кодек и битрейт.; Адаптировать композицию к другой форме кадра, сохраняя смысл, читаемость и доступность.; Проверять готовый файл, права и достоверность перед передачей на публикацию. | 9: — | no graded relation; no media |

### Ordering and relationship checks

**CONFIRMED:** Module order is contiguous within each course; lesson order is contiguous within each module. No empty module, lesson orphan, or lesson-order gap was found. Course 9 repeats title `123` in its two module records and has repeated placeholder lesson titles; this is a content-quality anomaly, not an ordering collision. Database auto-ID gaps (including absent former QA IDs) do not imply missing curriculum positions.

**CONFIRMED:** Course 1 has no module/lesson. Course 9 has two modules with title `123`, and three minimal lessons (`123`, `321`, `123`) with empty text bodies/structured learning content; one lesson has a one-question draft quiz. These records are incomplete for learning, though their intended status/ownership is **UNKNOWN**.

## D. Course 10 deep audit

**CONFIRMED:** Course 10 (`ai-media-content`) is an existing unpublished, open-enrollment, beginner course. It has five ordered modules and 15 lessons. Modules 1–4 each have three lessons and Module 5 has lessons 113–115. It has no course certificate policy, quiz records, or assignment records. Graded assessment is reserved to Module 6 in current course planning documents; no Module 6 exists. Lesson 115 has nine structured sections and three objectives, but no image or attachment records.

| Module order / title | Module ID | Lessons | Learning structure | Media inventory |
| 1 — Основы ИИ в медиапроизводстве | 34 | Как генеративный ИИ помогает создавать медиаконтент<br>Бриф, промпт и выбор ИИ-инструмента<br>Проверка фактов, права и прозрачность использования ИИ | 1 (ID 100): 3 objectives, 6 sections, 0 images, 0 attachments<br>2 (ID 101): 3 objectives, 6 sections, 0 images, 0 attachments<br>3 (ID 102): 3 objectives, 9 sections, 0 images, 0 attachments | — |
| 2 — Тексты и сценарии с помощью ИИ | 35 | Поиск идей и подготовка медиабрифа<br>Создание сценариев с помощью ИИ<br>Адаптация медиаконтента для разных площадок | 1 (ID 103): 3 objectives, 8 sections, 0 images, 0 attachments<br>2 (ID 104): 3 objectives, 9 sections, 0 images, 0 attachments<br>3 (ID 105): 3 objectives, 9 sections, 0 images, 0 attachments | — |
| 3 — Создание изображений и графики с помощью ИИ | 36 | Генерация изображений с помощью ИИ<br>Создание обложек, карточек и инфографики<br>Единый визуальный стиль медиапроекта | 1 (ID 106): 3 objectives, 9 sections, 2 images, 0 attachments<br>2 (ID 107): 3 objectives, 9 sections, 2 images, 0 attachments<br>3 (ID 108): 3 objectives, 9 sections, 2 images, 0 attachments | — |
| 4 — Создание и обработка аудио с помощью ИИ | 37 | Генерация речи и озвучка медиаматериалов<br>Распознавание речи и создание субтитров<br>Обработка звука и подготовка аудио для монтажа | 1 (ID 109): 3 objectives, 9 sections, 0 images, 1 attachments<br>2 (ID 110): 3 objectives, 9 sections, 0 images, 3 attachments<br>3 (ID 111): 3 objectives, 9 sections, 1 images, 2 attachments | — |
| 5 — Создание и монтаж видео в CapCut Desktop | 39 | Подготовка видеопроекта и организация материалов<br>Монтаж, озвучка и интеллектуальные инструменты<br>Экспорт, адаптация и подготовка видео к публикации | 1 (ID 113): 3 objectives, 9 sections, 0 images, 3 attachments<br>2 (ID 114): 3 objectives, 9 sections, 0 images, 5 attachments<br>3 (ID 115): 3 objectives, 9 sections, 0 images, 0 attachments | — |

### Lesson 115 planned media versus reality

**CONFIRMED:** `docs/courses/media-module-5-assets.json` plans three videos with associated VTT tracks, all marked `planned_not_created`; no hashes are declared. Planned placement anchors are:

- `m5-l15-v1-export-check.mp4` + `.vtt`, after section 3, `Экспорт проверочной версии в CapCut Desktop`.
- `m5-l15-v2-vertical-adaptation.mp4` + `.vtt`, after section 5, `Адаптация 16:9 в 9:16`.
- `m5-l15-v3-final-review.mp4` + `.vtt`, after section 7, `Редакторская проверка перед публикацией`.

**CONFIRMED:** No matching lesson-115 video or VTT files were found in the inspected `video-production/lesson-115-production/` and `course_assets/module_5/` locations; Lesson 115 has zero attachment rows. These are future production dependencies, not completed assets.

**CONFIRMED:** Lessons 113 and 114 have video integrations in SQLite. Lesson 113 has three video attachment records; Lesson 114 has three video records and two VTT tracks. Current stored attachment files exist, and DB SHA-256 values match file bytes and the applicable Module 5 asset manifest. Their integration reports and local integration commands are untracked working-tree artifacts; do not conflate their existence with Git-tracked source or with Lesson 115 completion. Course 10 remains unpublished.

## E. Source-of-truth mapping

| Content group | Canonical/source files and importer | Audit result / discrepancies |
|---|---|---|
| Courses 2–7 demo curriculum | `courses/management/demo_course_data.py`; `courses/management/commands/seed_demo_courses.py` | **CONFIRMED:** Course/module/lesson titles and text match the seeded objects. The seed command uses `update_or_create` and forces `is_published=True`, whereas the current six DB courses are unpublished. Re-running is not a harmless no-op: it can change publication state. Do not rerun without reviewing its effects. |
| Course 8 | `courses/management/first_course_content.json`; `course_sources/Глава_1_Выбор_ИИ_модели_и_сервиса.docx`; `courses/management/commands/import_first_course.py`; `docs/courses/first-course-implementation.md` | **CONFIRMED:** Source hash in CourseImport receipt matches DOCX. Lesson content/objectives/source sections match the import snapshot, except Lesson 92 interaction data: database matches the explicitly approved proposal `docs/courses/lesson92-content-edit-proposal.json`, while base JSON remains stale. Course and quiz publication states now differ from original draft source, documented as an approved later operational transition. The importer has conflict/fingerprint protection; it is not a general update tool. |
| Course 8 lesson 91 | `docs/courses/lesson91-content-edit-proposal.json`; `frontend/src/utils/lesson91Source.js`; `frontend/src/utils/lessonPresentation.js` | **CONFIRMED:** The DB still contains title-page text. The JSON proposal is marked proposal-only; frontend hides an exact source preface at presentation time. No DB content removal is inferred. |
| Course 10 Module 1 | `course_sources/media_module_1.docx`; `courses/management/commands/import_media_module.py`; CourseImport receipt | **CONFIRMED:** Receipt hash matches DOCX; all three lesson texts, titles, objectives and headings match the source plan exactly. |
| Course 10 Modules 2–5 | `courses/management/media_module_2.json` … `media_module_5.json`; `import_media_module_2.py` … `import_media_module_5.py` | **CONFIRMED:** All 12 DB lesson titles/text/objectives/headings match the canonical JSON snapshots. Lessons 113/114 DB text also matches the updated canonical Module 5 JSON. CourseImport review flag remains false. |
| Course 10 Module 3 images | `docs/courses/media-module-3-assets.json`; six PNGs in `course_assets/module_3/`; `import_media_module_3_images.py`; `place_media_module_3_images.py` | **CONFIRMED:** Six database images correspond to the six source PNGs; decoded pixels match and inline placements match the lesson interaction metadata. Manifest’s overall `status: planning_only_no_files_created` is stale and conflicts with actual files/DB records. Manifest identifies lessons by course-relative lesson 7–9 while DB IDs are 106–108; this appears to be curriculum-relative numbering, but should be made explicit. |
| Course 10 Module 4 | `courses/management/media_module_4.json`; `docs/courses/media-module-4-assets.json`; provenance docs; `import_media_module_4.py`, `finalize_module4_media.py` | **CONFIRMED:** Six attachment records plus one inline image match the seven manifest assets; stored files exist and hashes match DB + manifest. The course remains unpublished. Older `docs/courses/media-module-4.md` is an earlier plan and is not current state evidence. |
| Course 10 Module 5 / Lessons 113–115 | `courses/management/media_module_5.json`; `docs/courses/media-module-5-assets.json`; storyboards and completion docs; `integrate_lesson113_videos.py`, `integrate_lesson114_videos.py` | **CONFIRMED:** Canonical lesson text matches DB. Lessons 113/114 integration is present in DB and files; Lesson 115 assets remain planned and absent. Historical readiness/validation documents describe earlier phases and must be read with dates/status context. |
| Courses 1 and 9 | No matching canonical source located in inspected source set | **UNKNOWN:** Intended author, status and source are not established. Course 9 looks test-like but that does not prove disposable or accidental status. |

**CONFIRMED:** Module 5 metadata is not entirely synchronized: `docs/courses/media-module-5-assets.json` now reflects L13/L14 integrations and L15 pending media, while older phase notes still describe earlier importer/source status. There are also four modified tracked files, including Module 5 JSON/importer/manifest, so this report’s source comparison describes the current working-tree versions, not an immutable Git checkpoint.

## F. Assessments and completion

**CONFIRMED:** The database has four quizzes: Course 2 lesson 15 (published, 70%, 15 questions/60 choices); Course 7 lesson 88 (published, 70%, 2/8); Course 8 lesson 96 (published, 70%, 15/60); Course 9 lesson 97 (draft, 70%, 1/2). This audit intentionally did not inspect question wording, choices, correct answers or submissions.

**CONFIRMED:** There is one `Assignment` record: Course 8 Lesson 96, structured `ai_selection_map`. Assignment submission and review workflow is represented by `progress.AssignmentSubmission`, including status, review timestamps, reviewer comment and review history. No submission rows were queried. No Course 10 assignment exists.

**CONFIRMED:** Lesson completion is recorded independently in `progress.LessonProgress`; quiz attempts and assignment reviews are separate evidence. `CompleteLessonView` does not itself mean that a course’s assessment is passed. Course completion/certificate eligibility is policy-driven through `certificates.CourseCertificatePolicy` and `certificates.services.eligibility`: policy can require all lesson completions, a configured final quiz pass, and specified assignment approvals with attributable review evidence.

**CONFIRMED:** Only Course 8 has a certificate policy. It is enabled, issuer-approved, requires all lessons, references published quiz 3, and requires assignment 1. Course 10 has no policy; no certificate eligibility configuration exists for it. No certificate/student rows were inspected.

**Module 6 — UNKNOWN / not ready for implementation from current artifacts:** There is no Module 6 row, canonical content JSON, import command, assessment rubric, quiz, assignment specification, or Module 6 asset manifest. Existing Module 2–5 docs reserve graded assessment for Module 6 but do not establish lesson count, learning outcomes, grading thresholds, retake policy, assignment approval criteria or certificate policy. These are author decisions; do not invent them.

## G. Frontend content rendering map

| Student-facing concern | Backend/source | Frontend path | Static relationship and verification boundary |
|---|---|---|---|
| Catalog/course visibility | `courses.Course`, course list/detail API views | `frontend/src/pages/CourseCatalog.jsx`, `CourseDetail.jsx` | Catalog loads course list; course detail displays API description and curriculum. Static source reviewed only, not run in browser. |
| Module and lesson navigation | `courses.Module`, `courses.Lesson`, lesson outline/curriculum APIs | `frontend/src/pages/CourseDetail.jsx`, `frontend/src/pages/LessonView.jsx`, `frontend/src/utils/lessons.js` | Ordered module/lesson data feeds course outline and previous/next navigation. Database ordering checked; actual runtime display not verified. |
| Objectives and structured sections | `courses.LessonLearningContent` objectives/source_sections; `Lesson.text_content` | `frontend/src/components/LearningContent.jsx`, `MediaLessonReading.jsx`, `utils/mediaLessonPresentation.js` | Structured headings are validated against paragraph headings; reusable renderer uses section blocks when valid and fallback when not. No browser behavior claimed. |
| Special Course 8 presentation | Lesson 91/92 content and proposal metadata | `frontend/src/utils/lesson91Source.js`, `lessonPresentation.js`, course8 reading components | Lesson91 has exact source-preface display handling. Lesson92 interaction display is approved DB content; base JSON is stale. |
| Inline images/audio/video/downloads | `LessonImage`, `LessonAttachment`, protected delivery APIs | `ProtectedLessonImage.jsx`, `LessonAttachment.jsx`, `LessonVideo.jsx`, `utils/lessonAttachments.js`, `utils/lessonVideo.js` | Image/audio/video use existing protected-media mechanisms; section anchors place media inline, with fallback for unplaced assets. Attachments and bytes were stat/hash checked; no browser playback was performed. |
| Assessment | `quizzes.Quiz/QuizQuestion/QuizChoice/QuizAttempt`; `courses.Assignment`; `progress.AssignmentSubmission` | `frontend/src/components/Quiz*.jsx`, `StructuredAssignment*.jsx`, `pages/instructor/Submissions.jsx` | Quiz API omits correct-answer fields; frontend guards quiz payload. Assignment student draft/submit and instructor review are separate flows. Protected workflow was static-inspected only. |
| Progress and certificates | `progress.LessonProgress`, enrollment; `certificates.CourseCertificatePolicy` | `frontend/src/pages/Profile.jsx`, `LessonView.jsx`, certificate components | Lesson check-off, enrollment status and certificate status are separate UI/data paths. No user-specific progress was read or browser-tested. |

**CONFIRMED limitation:** This phase did not launch a browser, make authenticated requests or inspect learner-specific pages. Therefore layout, console/network health, media playback, actual accessibility tree, and visible user-specific progress remain **UNKNOWN**. No screenshots were created.

## H. Content completeness and discrepancies

1. **CONFIRMED — sparse records:** Course 1 has no curriculum; Course 9 has three empty-body placeholder lessons and duplicate-looking placeholder titles. Author intent is **UNKNOWN**; preserve until confirmed.
2. **CONFIRMED — stale media manifest:** Module 3 asset manifest still declares a planning-only/no-files status although six real images are attached and placed. Correct the manifest in a separately approved content-maintenance task.
3. **CONFIRMED — Course 10 description drift:** The course-level description still describes Module 1 as the whole course despite five imported modules. Review editorially before course publication.
4. **CONFIRMED — stale Course 8 base interaction:** Lesson92 DB has approved distinct steps while `first_course_content.json` retains generic step text. The importer’s conflict guard prevents safe reimport, but source snapshots can mislead later maintainers. Reconcile canonical source through an explicit, idempotent approved content update, not a full reimport.
5. **CONFIRMED — planned versus integrated media:** L15 has no attachments and planned videos/VTT are absent. L13/L14 media are present; do not mark L15 complete.
6. **CONFIRMED — multiple historical docs:** Course Modules 4–5 contain phase artifacts whose claims were true when written but are stale now. Prefer explicitly dated completion reports/current manifests for state; consider a doc index/status banner.
7. **UNKNOWN — courses 1/9 provenance:** No source of truth was found. Need owner confirmation before cleanup or replacement.
8. **UNKNOWN — course 10 final assessment plan:** Module6 content and assessment/certificate rules have not been specified.

## I. Prioritized findings and next-stage recommendations

| Priority | Finding | Recommended next step |
|---|---|---|
| P0 | Course 10 remains unpublished; no Module 6 assessment/certificate policy is configured. | Keep it unpublished. Have the content owner define Module 6 outcomes, graded tasks, rubric, quiz rules, review/retake policy and certificate evidence before implementation. |
| P1 | Lesson 115 three videos + VTT tracks are plans only; no attachment records or files exist. | Produce/review actual recordings, validate duration/transcripts/subtitles, then use existing protected attachment workflow with backup and dry-run. |
| P1 | Course 10 description and Module 3 asset-manifest status are stale. | Approve small metadata-only source/manifest corrections; avoid lesson-content rewrite or database reimport. |
| P1 | Course8 approved Lesson92 database content differs from canonical JSON. | Create a narrowly scoped idempotent source reconciliation and test on isolated DB before any future importer maintenance. |
| P2 | Course 1 and 9 contain test-looking/incomplete records with unknown ownership. | Confirm owner and intended retention before archiving or editing; never infer disposable from titles. |
| P2 | `seed_demo_courses` forces publication on rerun. | Add explicit safeguards or change the command in a separately reviewed task so an educational content seed cannot silently publish courses. |
| P2 | Historical course docs can obscure current state. | Add clear “historical/planning/completed” status and date references; retain historical records. |

## J. Limitations and reproducibility

- No browser tests, frontend tests, lint, builds, Django test suite, API calls or imports were run. Audit-only read operations avoided test DB side effects. Static renderer/API mapping is not proof of live behavior.
- No learner accounts, enrollments, submission contents, reviewer details, quiz answers, attempts or certificate records were read. The assessment inventory reports configuration/counts only.
- The private quiz-import JSON was not opened. Course 2’s original private import provenance is therefore not audited.
- No course-1/course-9 source documents were found in the inspected paths; absence elsewhere is not proven.
- Media verification was metadata/hash/pixel comparison only, not human viewing/listening or browser playback.
- Database status represents the local `db.sqlite3` snapshot on 2026-11-09, not production or another deployment.

## K. Working-tree status and no-change confirmation

**Before report creation:** branch `design/amethyst-motion`, ahead four; four modified tracked files: `config/settings.py`, `courses/management/commands/import_media_module_5.py`, `courses/management/media_module_5.json`, `docs/courses/media-module-5-assets.json`; numerous pre-existing untracked work files including `docs/project-audit/01-technical-inventory.md`. No staged changes.

**After report creation:** the above status remains unchanged except this authorized report file has been added under the already-untracked `docs/project-audit/` directory. No files outside that target were written. No database records or SQLite bytes were modified. No stage, commit or push was performed.
