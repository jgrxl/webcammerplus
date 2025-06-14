# Claude Code Engineering Principles Guide

## Instructions for Better Technical Decision Making

When implementing any technical solution or infrastructure, follow these engineering principles:

### 1. SIMPLE OVER COMPLEX
Start with the simplest solution that solves the problem. Don't over-engineer or try to handle every edge case immediately.

### 2. WORK WITH EXISTING ARCHITECTURE
Respect the current project structure and patterns. Don't restructure or refactor unless specifically asked. Build on what's already there.

### 3. MODULAR DESIGN
Break complex tasks into smaller, focused components. Each piece should have a single clear responsibility and be independently testable.

### 4. TEST INCREMENTALLY
Implement and test one piece at a time. Verify each component works before adding the next. Always test locally before pushing changes.

### 5. PRACTICAL VALUE
Focus on solutions that provide real, immediate benefit. Avoid adding tools, dependencies, or complexity unless there's a clear need and justification.

### 6. HUMAN-FRIENDLY DECISIONS
Make choices that are easy for humans to understand, maintain, and debug. Prefer explicit over clever, readable over concise.

### 7. FAIL GRACEFULLY
When something doesn't work, identify the specific issue and fix it narrowly rather than rebuilding everything.

### 8. ASK CLARIFYING QUESTIONS
If a task seems to require major changes or complex solutions, ask for clarification about the real requirements and constraints.

### 9. DOCUMENT REASONING
Explain why you're making specific technical choices, especially when there are multiple valid approaches.

---

## Core Philosophy

**Remember:** The best technical solution is the one that solves the actual problem with minimal complexity and maximum maintainability. Optimize for human understanding and long-term sustainability, not theoretical perfection.

---

## Usage Instructions

Copy and paste these principles into Claude Code at the beginning of any technical project to ensure better engineering decisions and more maintainable solutions.

**Created:** Based on lessons learned from real-world AI engineering collaboration  
**Purpose:** Guide AI tools toward practical, human-friendly technical solutions