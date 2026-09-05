# `help-me-learn` --- ADHD-Friendly Adaptive Learning Research Notes

> **Purpose:** Capture the key insights from the Reddit discussion and
> translate them into design principles for the `help-me-learn` skill.
>
> **Important:** These are learning-support ideas and community
> experiences, not medical advice or a substitute for professional ADHD
> care.

------------------------------------------------------------------------

## 1. Core Observation

There is **no single ADHD study method** that works for everyone.

Different learners may need opposite conditions:

-   Silence vs. background sound
-   Short timers vs. longer uninterrupted focus
-   Studying alone vs. body doubling
-   Detailed planning vs. minimal planning
-   Fixed environments vs. changing locations

### Design Principle

> **Personal experimentation should beat universal prescriptions.**

`help-me-learn` should discover what works for the individual learner
instead of assuming one ADHD-specific workflow.

------------------------------------------------------------------------

## 2. ADHD Learning Is More Than a "Focus Problem"

The difficulties described by learners can occur at multiple stages:

``` text
Starting
   ↓
Directing attention
   ↓
Sustaining attention
   ↓
Resisting distractions
   ↓
Organizing
   ↓
Remembering
   ↓
Estimating workload/time
   ↓
Maintaining motivation
   ↓
Recovering after losing focus
```

The system should identify **which barrier is happening now** before
choosing an intervention.

------------------------------------------------------------------------

## 3. Task Initiation Is Its Own Problem

A learner may:

``` text
Know what needs to be done
        ↓
Want to do it
        ↓
Still struggle to start
```

Large or ambiguous tasks increase activation cost.

Instead of:

``` text
Study Chapter 3
```

reduce the task:

``` text
Open Chapter 3
→ Find the first heading
→ Read one paragraph
→ Answer one question
```

### Activation Engine

``` text
Large Task
    ↓
Find smallest executable action
    ↓
Reduce friction
    ↓
Get first success
    ↓
Build momentum
```

------------------------------------------------------------------------

## 4. Attention Regulation, Not Just "Focus Harder"

Environmental preferences differ significantly.

Possible conditions to experiment with:

-   Complete silence
-   Noise-blocking headphones
-   Instrumental music
-   Ambient noise
-   Lo-fi
-   Library/public study environment
-   Studying near other productive people

Never hard-code:

``` text
ADHD → Use Lo-fi
```

Instead:

``` text
Environment A: Silence
Environment B: Instrumental audio
Environment C: Ambient noise
Environment D: Library

        ↓

Observe which environment helps this learner.
```

------------------------------------------------------------------------

## 5. Environment Is Part of the Learning System

The learning agent should consider whether the environment itself
creates unnecessary friction.

Example learner state:

``` yaml
environment:
  location: home
  phone_distraction: high
  noise_preference: unknown
  social_presence_helpful: true
  preferred_audio: unknown
```

Possible interventions:

-   Silence notifications
-   Move the phone away
-   Change location
-   Use headphones
-   Prepare materials before starting
-   Study around other focused people

The agent should **learn these preferences over time**.

------------------------------------------------------------------------

## 6. Externalize Memory and Organization

Do not require working memory to manage everything.

Useful external systems mentioned or implied by learners include:

-   Calendars
-   Whiteboards
-   Visible deadlines
-   Task lists
-   Digital notes
-   Flashcards
-   Anki
-   Mind maps
-   Weekly planning
-   Written reminders

Instead of:

``` text
BRAIN

Remember assignment
Remember deadline
Remember next task
Remember review
Remember materials
Remember what was studied
Remember what was forgotten
```

use:

``` text
             LEARNER
                │
       ┌────────┼────────┐
       ↓        ↓        ↓
    Calendar   Tasks    Notes
       │        │        │
       ↓        ↓        ↓
  Deadlines   Actions   Knowledge
```

### Agent Opportunity

The AI can remember:

-   Current learning position
-   Weak concepts
-   Previous mistakes
-   Next learning action
-   Review schedule
-   Preferred study conditions

The learner should not repeatedly ask:

> "Where was I?"

------------------------------------------------------------------------

## 7. Body Doubling and Accountability

Some learners benefit from studying:

-   With another person
-   Around other students
-   In libraries
-   With "study with me" sessions
-   Through scheduled accountability meetings

### AI Body-Double Mode

``` text
Agent:
We are only doing Step 1.

        ↓

Learner completes Step 1.

        ↓

Agent:
Without looking, tell me the two main ideas.

        ↓

Learner answers.

        ↓

Agent evaluates understanding.

        ↓

Next small task.
```

The AI should become an **interactive learning companion**, not merely
an information generator.

------------------------------------------------------------------------

## 8. Adaptive Timeboxing

Different learners may benefit from different focus cycles:

``` text
15 / 5
20 / flexible break
25 / 5
50 / 10
```

Avoid assuming:

``` text
ADHD_MODE = Pomodoro(25, 5)
```

Instead:

``` text
Estimate attention capacity
        ↓
Choose initial focus block
        ↓
Observe completion
        ↓
Was it too difficult?
      /       \
    Yes        No
     ↓          ↓
 Shorten    Maintain/increase
```

### Important Rule

Do not interrupt productive concentration simply because a timer reached
an arbitrary number.

------------------------------------------------------------------------

## 9. Interest Engine

Low-interest topics can be especially difficult to initiate or sustain.

The agent should create relevance before dumping information.

``` text
Topic
  ↓
Why should the learner care?
  ↓
Connect to existing interests/goals
  ↓
Present a concrete problem
  ↓
Create curiosity
  ↓
Teach concept
  ↓
Immediate application
```

Instead of:

> "Today we will study probability distributions."

Try:

> "An AI model says it is 90% confident. What does that actually mean,
> and when should you distrust it?"

### Goal

Turn:

``` text
Abstract Topic
```

into:

``` text
Question → Curiosity → Knowledge → Application
```

------------------------------------------------------------------------

## 10. Realistic Planning

Avoid planning around the maximum amount of work theoretically possible.

Bad:

``` text
Monday

Python     2h
Math       2h
English    1h
AI         2h
Reading    1h
Exercise   1h
```

Better:

``` text
MUST
├── Complete Python lesson
└── Finish required math exercises

SHOULD
└── Review flashcards

COULD
└── Read one AI article
```

### Principle

> Optimize for sustainable completion, not maximum theoretical
> productivity.

Plans should include:

-   Free space
-   Recovery time
-   Flexibility
-   Priorities
-   Realistic workload

------------------------------------------------------------------------

## 11. Recovery Must Be a First-Class Feature

Traditional productivity systems often assume:

``` text
Plan → Execute → Success
```

Real learning can look more like:

``` text
Plan
 ↓
Start
 ↓
Distracted
 ↓
Return
 ↓
Confused
 ↓
Break
 ↓
Restart
 ↓
Progress
 ↓
Routine disappears for several days
 ↓
Return
```

The system must support **re-entry**.

Bad response:

> "You missed three sessions and have 47 overdue reviews."

Better response:

> "Last time you were learning X. Let's spend five minutes checking what
> you still remember, then rebuild today's session from there."

### Recovery Engine Handles

-   "I'm lost."
-   "I forgot everything."
-   "I'm overwhelmed."
-   "I haven't studied for a week."
-   "I don't know where I stopped."
-   "I'm bored."
-   "I can't start."

------------------------------------------------------------------------

## 12. Avoid Productivity-System Obsession

A learner can accidentally replace studying with designing a study
system.

``` text
Can't study
   ↓
Research study methods
   ↓
Install productivity app
   ↓
Build dashboard
   ↓
Configure notes
   ↓
Download flashcards
   ↓
Watch productivity videos
   ↓
Hours later...
   ↓
Still haven't studied
```

### Meta-Learning Budget

The agent should sometimes say:

> "The current system is good enough. Don't optimize it right now. Start
> the lesson."

`help-me-learn` should prevent endless optimization from becoming
avoidance.

------------------------------------------------------------------------

# Proposed `help-me-learn` Architecture

``` text
                 LEARNER
                    │
                    ↓
          ┌───────────────────┐
          │ Learner Profiler  │
          └─────────┬─────────┘
                    ↓
     ┌─────────────────────────────┐
     │ Current State Detection     │
     │                             │
     │ attention                   │
     │ energy                      │
     │ interest                    │
     │ knowledge                   │
     │ overwhelm                   │
     │ available time              │
     │ environment                 │
     └──────────────┬──────────────┘
                    ↓
             Identify Barrier
                    ↓
    ┌───────────────┼────────────────┐
    ↓               ↓                ↓
 Can't Start    Can't Focus      Don't Understand
    ↓               ↓                ↓
 Micro-task     Environment       Scaffolding
 Friction ↓     Timeboxing        Prerequisite check
 Momentum       Body doubling     New representation
    │               │                │
    └───────────────┼────────────────┘
                    ↓
              LEARNING ENGINE
                    ↓
       ┌────────────────────────┐
       │ Explain                │
       │ Question               │
       │ Retrieve               │
       │ Practice               │
       │ Apply                  │
       │ Assess                 │
       └───────────┬────────────┘
                   ↓
             Observe Result
                   ↓
                 Adapt
                   ↓
            Update Learner Model
                   │
                   └──────────→ Repeat
```

------------------------------------------------------------------------

# Six Adaptive Engines

## 1. Attention Engine

Responsible for:

-   Focus-session length
-   Break strategy
-   Environmental experiments
-   Distraction reduction
-   Detecting declining attention
-   Protecting productive focus

------------------------------------------------------------------------

## 2. Activation Engine

Responsible for helping the learner **start**.

``` text
Task
 ↓
Reduce ambiguity
 ↓
Reduce size
 ↓
Define first physical/executable action
 ↓
Start
 ↓
Create momentum
```

------------------------------------------------------------------------

## 3. Interest Engine

Responsible for making low-interest material more engaging through:

-   Existing interests
-   Goals
-   Real-world problems
-   Curiosity gaps
-   Challenges
-   Immediate application
-   Choice

------------------------------------------------------------------------

## 4. Learning Engine

Chooses appropriate techniques, including:

-   Active recall
-   Retrieval practice
-   Feynman technique
-   Chunking
-   Scaffolding
-   Worked examples
-   Deliberate practice
-   Interleaving
-   Project-based learning
-   Practice questions
-   Visualization
-   Teaching/explanation

The engine should choose methods according to the learner and topic
rather than use every technique every time.

------------------------------------------------------------------------

## 5. Memory Engine

Responsible for:

-   Tracking previously learned concepts
-   Detecting weak knowledge
-   Scheduling retrieval
-   Spaced review
-   Remembering mistakes
-   Connecting new knowledge to previous knowledge
-   Determining what should be reviewed next

------------------------------------------------------------------------

## 6. Recovery Engine

Responsible for helping learners return after:

-   Distraction
-   Confusion
-   Overwhelm
-   Loss of motivation
-   Long breaks
-   Forgotten material
-   Failed plans

### Recovery Philosophy

``` text
Failure to follow plan
        ↓
Do NOT punish learner
        ↓
Diagnose what failed
        ↓
Modify system
        ↓
Create smallest restart action
        ↓
Continue
```

------------------------------------------------------------------------

# Learner Model

``` yaml
learner:
  prior_knowledge: unknown
  confidence: unknown

  attention:
    capacity: unknown
    distraction_level: unknown
    preferred_session_length: unknown

  motivation:
    current_level: unknown
    topic_interest: unknown

  cognitive_load:
    current_level: unknown

  environment:
    location: unknown
    noise_preference: unknown
    phone_distraction: unknown
    body_doubling_helpful: unknown

  learning_preferences:
    visual: unknown
    examples: unknown
    practice: unknown
    explanation_depth: unknown

  available_time: unknown

  progress:
    current_topic: unknown
    weak_concepts: []
    strong_concepts: []
    next_action: unknown
```

------------------------------------------------------------------------

# Current-State Detection

Before choosing a strategy, identify the current barrier.

``` text
What is stopping progress RIGHT NOW?
```

Possible states:

``` yaml
state:
  cannot_start: false
  distracted: false
  bored: false
  overwhelmed: false
  confused: false
  tired: false
  forgotten_previous_material: false
  productive_focus: false
```

Do not treat every state as the same "focus problem."

------------------------------------------------------------------------

# Adaptive Response Examples

## "I'm lost"

``` text
Stop introducing new information
        ↓
Find last understood concept
        ↓
Locate knowledge gap
        ↓
Change explanation/representation
        ↓
Give one tiny exercise
        ↓
Check understanding
        ↓
Continue
```

------------------------------------------------------------------------

## "I'm bored"

Do not automatically simplify.

``` text
Why is the learner bored?
        ↓
┌───────────────┬─────────────────┐
↓               ↓                 ↓
Too Easy    Too Abstract      Too Passive
↓               ↓                 ↓
Increase     Concrete          Interactive
difficulty   application       activity
```

Other possibilities:

``` text
Session too long → shorten it
No relevance    → connect to learner's goal
Repetitive      → change activity
```

------------------------------------------------------------------------

## "I can't start"

``` text
Reduce task
    ↓
Define first action
    ↓
Remove preparation friction
    ↓
Start a tiny commitment
    ↓
Build momentum
```

------------------------------------------------------------------------

## "I forgot everything"

``` text
Do NOT restart entire course
        ↓
Run quick retrieval check
        ↓
Identify retained knowledge
        ↓
Identify missing knowledge
        ↓
Review only necessary gaps
        ↓
Continue
```

------------------------------------------------------------------------

# Mastery Model

Do not mark something as learned simply because it was presented.

``` text
Recognize
    ↓
Understand
    ↓
Recall
    ↓
Explain
    ↓
Apply
    ↓
Transfer
    ↓
Independent Mastery
```

Possible progress representation:

``` text
Topic: Example Concept

Exposure       ██████████ 100%
Understanding  ████████░░  80%
Recall         ██████░░░░  60%
Application    █████░░░░░  50%
Independence   ███░░░░░░░  30%
```

------------------------------------------------------------------------

# Core Adaptive Loop

``` text
OBSERVE
   ↓
MODEL LEARNER
   ↓
IDENTIFY CURRENT BARRIER
   ↓
SELECT STRATEGY
   ↓
TEACH / GUIDE
   ↓
INTERACT
   ↓
RETRIEVE / PRACTICE
   ↓
ASSESS
   ↓
ADAPT
   ↓
REINFORCE
   ↓
UPDATE LEARNER MODEL
   ↺
```

------------------------------------------------------------------------

# Fundamental Principles for `help-me-learn`

1.  **Adapt the learning experience to the learner.**
2.  Do not assume every learner with ADHD needs the same strategy.
3.  Identify the current barrier before recommending a solution.
4.  Reduce activation cost when starting is difficult.
5.  Prefer small executable actions over vague large goals.
6.  Externalize memory and organization.
7.  Experiment with environment instead of prescribing one environment.
8.  Adapt focus duration instead of enforcing one timer.
9.  Protect productive concentration.
10. Create relevance when interest is low.
11. Prefer active learning over passive information consumption.
12. Measure understanding, recall, application, and independence
    separately.
13. Make recovery easy after interruptions or failed plans.
14. Do not punish missed sessions with overwhelming backlogs.
15. Avoid turning productivity-system optimization into procrastination.
16. Remember what works for the individual learner.
17. Continuously update the learner model from observed results.
18. Treat community experiences as hypotheses to test, not universal
    facts.

------------------------------------------------------------------------

# Skill Philosophy

> **Do not force the learner to adapt to the course. Adapt the learning
> experience to the learner.**

The objective of `help-me-learn` is not merely to present information.

Its objective is to help the learner progress through:

``` text
Start
 ↓
Engage
 ↓
Understand
 ↓
Retrieve
 ↓
Apply
 ↓
Retain
 ↓
Transfer
 ↓
Become Independent
```

while minimizing unnecessary cognitive and organizational friction.

------------------------------------------------------------------------

## Source

The initial community insights summarized in these notes were inspired
by the Reddit discussion:

**r/ADHD --- "How do you study as an ADHD student? How do you get things
done and what keeps you going?"**

https://www.reddit.com/r/ADHD/comments/1elaqrc/how_do_you_study_as_an_adhd_student_how_do_you/
