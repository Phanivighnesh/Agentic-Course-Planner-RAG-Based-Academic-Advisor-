# 🎓 Sample Inputs to Try on the Streamlit App
# Institution: Georgia Tech | Catalog: 2024-2025

=========================================================
SIDEBAR PROFILE SETUP (fill this in first, click Save)
=========================================================

Target Program:   B.S. Computer Science
Catalog Year:     2024-2025
Max Credits:      15

=========================================================
SCENARIO A — Freshman (just completed CS 1301)
=========================================================

Completed Courses:  CS 1301
Grades:             CS 1301:B+
Target Term:        Fall 2025

--- Try these chat inputs ---

1. "What courses can I take next semester with only CS 1301 done?"

2. "Can I enroll in CS 1332 (Data Structures) next semester?"
   → Expected: NOT eligible — CS 1331 is missing

3. "What is the full prerequisite chain to reach CS 4641 (Machine Learning)
   starting from where I am now?"
   → Expected: Multi-hop chain: CS 1331 → CS 1332 → CS 3600 → CS 4641

4. "Plan my Fall 2025 schedule — I've completed CS 1301 with a B+, 
   targeting B.S. CS, max 15 credits."

=========================================================
SCENARIO B — Sophomore (completed core intro courses)
=========================================================

Completed Courses:  CS 1301, CS 1331, CS 1332, CS 2050, MATH 1551, MATH 1552
Grades:             CS 1301:A, CS 1331:B+, CS 1332:B, CS 2050:A-, MATH 1551:A, MATH 1552:B+
Target Term:        Fall 2025

--- Try these chat inputs ---

5. "Am I eligible to take CS 3510 (Algorithms) this fall?"
   → Expected: YES — CS 1332 ✅ and CS 2050 ✅ both done with C+

6. "Can I take CS 3600 (Intro to AI) this semester?"
   → Expected: YES — only needs CS 1332

7. "I want to take both CS 3510 and CS 3600 this fall. Is that possible?
   I have CS 1332 and CS 2050 done."

8. "Plan my Fall 2025 courses. Completed: CS 1301, CS 1331, CS 1332,
   CS 2050, MATH 1551, MATH 1552. Target: Intelligence Thread. Max 15 credits."

=========================================================
SCENARIO C — Junior (Intelligence Thread student)
=========================================================

Completed Courses:  CS 1301, CS 1331, CS 1332, CS 2050, CS 2110, CS 2200,
                    CS 2340, CS 3510, CS 3600, MATH 1554, MATH 2603
Grades:             All A or B except CS 2110:C+
Target Term:        Spring 2026

--- Try these chat inputs ---

9. "Am I eligible for CS 4641 (Machine Learning) in Spring 2026?"
   → Expected: YES — CS 3600 ✅, MATH 2603 ✅

10. "What do I still need to complete the Intelligence Thread?"

11. "Can I take CS 4650 (NLP) and CS 4641 (ML) in the same semester?"

12. "I got a C+ in CS 2110. Does that satisfy the prerequisite for CS 2200?"
    → Expected: YES — C or better means C+ qualifies

=========================================================
SCENARIO D — Prerequisite edge cases
=========================================================

Completed Courses:  CS 1301, CS 1331
Grades:             CS 1301:A, CS 1331:D
Target Term:        Fall 2025

--- Try these chat inputs ---

13. "I passed CS 1331 with a D. Can I now take CS 1332?"
    → Expected: NOT eligible — D does not satisfy the C-or-better prerequisite

14. "I failed CS 1331 and want to retake it. What is Georgia Tech's repeat policy?"
    → Expected: Cite grade replacement policy, max repeat rules

15. "I got a D in CS 1331. Can I get instructor consent to take CS 1332 anyway?"
    → Expected: Cite instructor consent exception — possible but not guaranteed

=========================================================
SCENARIO E — Abstention / Trick Questions (should get "I don't know")
=========================================================

16. "Is CS 3600 offered in Fall 2025 or only Spring?"
    → Expected: ABSTAIN — availability per term not in catalog

17. "Who teaches CS 4641 next semester?"
    → Expected: ABSTAIN — professor assignments not in catalog

18. "What is the tuition per credit hour at Georgia Tech?"
    → Expected: ABSTAIN — tuition not in academic catalog

19. "Is there a waitlist for CS 3510?"
    → Expected: ABSTAIN — waitlist process not in catalog

20. "Can Professor Smith waive my CS 2050 prerequisite for CS 3510?"
    → Expected: Partial answer citing instructor consent exception, 
                then ABSTAIN on professor-specific approval details

=========================================================
SCENARIO F — Program requirement questions
=========================================================

Set profile: Completed Courses empty, Target Program: B.S. Computer Science

21. "How many total credits do I need to graduate with a B.S. in CS at Georgia Tech?"
    → Expected: 120 credit hours, with citation

22. "How many threads do I need to complete and what are my options?"
    → Expected: 2 threads from 9 options, list them, cite catalog

23. "What is the minimum grade I need in each course to count it toward my degree?"
    → Expected: C or better, cite minimum grade policy

24. "Can I take any course on a pass/fail basis?"
    → Expected: Up to 6 free elective hours may be pass/fail; required CS courses must be letter grade

25. "How many credit hours must I take at Georgia Tech itself (residency requirement)?"
    → Expected: 36 hours in residence, with citation

=========================================================
MULTI-TURN CONVERSATION EXAMPLE
=========================================================

Turn 1: "I've completed CS 1301 and CS 1331. What should I take next fall?"
Turn 2: "Which of those courses counts toward the Intelligence Thread?"
Turn 3: "What's the full path from CS 1332 to being ready for CS 4641?"
Turn 4: "If I take CS 1332 and CS 2050 this fall, am I on track?"

This tests whether the assistant maintains context across turns.
