# Learning Hub V3 — User Workflows & Flow Diagrams

This document details the step-by-step workflows for major user journeys in **Learning Hub V3**, including happy paths, alternative paths, and error states.

---

## 1. Learner Authentication & Portal Entry

```mermaid
flowchart TD
    Start([Learner Accesses /learner/login]) --> EnterID[Enter Global ID e.g. 10001]
    EnterID --> Submit{Submit Form}
    Submit -->|Valid ID| FindLearner[Find Learner in DB]
    Submit -->|Invalid ID| ErrMsg[Display Error: Learner Not Found]
    ErrMsg --> EnterID
    FindLearner --> StreakCheck{Check Last Active Date}
    StreakCheck -->|Logged in today| MaintainStreak[Keep Current Streak]
    StreakCheck -->|Yesterday| IncStreak[Increment Streak + Award Points]
    StreakCheck -->|Older| ResetStreak[Reset Streak to 1 + Award Login Points]
    IncStreak --> CheckBadge{Streak >= 5?}
    CheckBadge -->|Yes| AwardBadge[Award Streak Master Badge]
    CheckBadge -->|No| Portal[Redirect to /learners/portal]
    AwardBadge --> Portal
    MaintainStreak --> Portal
    ResetStreak --> Portal
```

---

## 2. Self-Paced Course Completion & Certification Flow

```mermaid
flowchart TD
    Portal[Learner Portal] --> SelectCourse[Select Self-Paced Course]
    SelectCourse --> CheckPreAss{Pre-Assessment Exists?}
    CheckPreAss -->|Yes| TakePre[Take Pre-Course Assessment]
    CheckPreAss -->|No| WatchLessons[View Lesson Content / Video / SCORM]
    TakePre --> WatchLessons
    WatchLessons --> CheckMinTime{Spent Min Time on Lesson?}
    CheckMinTime -->|No| WaitTime[Display Time Remaining Banner]
    WaitTime --> WatchLessons
    CheckMinTime -->|Yes| LessonAss{Lesson Assessment Exists?}
    LessonAss -->|Yes| TakeLessonAss[Submit MCQ Answers]
    LessonAss -->|No| NextLesson{More Lessons?}
    TakeLessonAss -->|Score < 80%| RetryAss[Retry Assessment max 3 attempts]
    RetryAss --> TakeLessonAss
    TakeLessonAss -->|Score >= 80%| NextLesson
    NextLesson -->|Yes| WatchLessons
    NextLesson -->|No| TakePost[Take Final Post-Course Assessment]
    TakePost --> CheckScore{Score >= Pass Percentage?}
    CheckScore -->|No| Fail[Mark Status: Failed / Retry]
    CheckScore -->|Yes| FeedbackSurvey[Redirect to Feedback Survey]
    FeedbackSurvey --> SubmitFeedback[Submit Survey Responses]
    SubmitFeedback --> Complete[Mark Status: Completed & Award Points]
    Complete --> GenCert[Generate ReportLab PDF Certificate]
    GenCert --> DownloadCert([Download CERT-XXXXXX.pdf])
```

---

## 3. Live Class QR Attendance & Audit Override Flow

```mermaid
flowchart TD
    Facilitator[Facilitator opens /attendance/qr_view/CLASS_ID] --> DisplayQR[Display QR Code on Screen]
    DisplayQR --> LearnerScan[Learner scans QR code via Mobile Browser]
    LearnerScan --> CheckAuth{Learner Logged In?}
    CheckAuth -->|No| RedirectLogin[Redirect to Learner Login with classId param]
    RedirectLogin --> LearnerScan
    CheckAuth -->|Yes| VerifyRoster{Learner in Class Roster?}
    VerifyRoster -->|No| Denied[Display Error: Not Enrolled in Class]
    VerifyRoster -->|Yes| MarkAttendance[Record Attendance: Present, QR]
    MarkAttendance --> Success([Display Green Confirmation Screen])

    subgraph Admin Manual Override & Audit
    Admin[Admin opens /attendance/manual/CLASS_ID] --> UpdateStatus[Select Learner & Change Status]
    UpdateStatus --> EnterReason[Enter Mandatory Reason]
    EnterReason --> SaveAudit[Save Attendance & Write AuditLog]
    end
```

---

## 4. Support Ticket Resolution Flow

```mermaid
flowchart TD
    Learner[Learner in Portal] --> ClickHelp[Click Support / Report Issue]
    ClickHelp --> FillForm[Select Category: Technical/Content/Certificate & Enter Description]
    FillForm --> SubmitIssue[Create LmsIssue Record status=Open]
    SubmitIssue --> AdminView[Admin views /learners/issues]
    AdminView --> ReviewTicket[Review Issue Details]
    ReviewTicket --> ClickResolve[Click Resolve Ticket]
    ClickResolve --> UpdateDB[Update LmsIssue status=Resolved & set resolved_at]
    UpdateDB --> NotifLearner([Learner sees ticket marked Resolved])
```
