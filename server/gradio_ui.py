"""
Gradio web UI for BugLab.
Provides interactive interface for testing the environment.
"""

import gradio as gr
from server.environment import PythonDebugEnvironment
from models import DebugAction
from server.grader import humanize_quality_feedback

# Global environment instance
env = None


def initialize_env():
    """Initialize the environment."""
    global env
    if env is None:
        env = PythonDebugEnvironment()
    return env


def reset_env():
    """Reset the environment and return a new problem."""
    try:
        env = initialize_env()
        obs = env.reset()
        
        problem_id = obs.problem_id
        description = obs.description
        buggy_code = obs.buggy_code
        difficulty = obs.difficulty
        
        status = f"**Problem ID:** {problem_id}\n**Difficulty:** {difficulty}"
        return (
            description,
            buggy_code,
            status,
            ""
        )
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return (error_msg, "", "Error", "")


def step_env(fixed_code: str):
    """Submit a code fix and get the result."""
    try:
        if not fixed_code.strip():
            return "Please enter code to submit.", "", ""
        
        env = initialize_env()
        
        # Auto-reset if no problem is loaded yet
        if env.current_problem is None:
            env.reset()
        
        action = DebugAction(fixed_code=fixed_code)
        obs = env.step(action)
        
        reward = obs.reward
        test_score = obs.test_score
        quality_score = obs.quality_score
        quality_feedback = obs.quality_feedback
        done = obs.done
        error_summary = obs.error_summary
        attempt = obs.attempt
        max_attempts = obs.max_attempts
        
        
        # Create user-friendly feedback
        test_percent = int(test_score * 100)
        quality_percent = int(quality_score * 100)
        reward_percent = int(reward * 100)
        
        # Determine status emoji and message
        if reward >= 0.9:
            status_emoji = "🎉"
            status_msg = "Excellent! Your fix is nearly perfect!"
        elif reward >= 0.7:
            status_emoji = "✅"
            status_msg = "Great job! Your fix works well!"
        elif reward >= 0.5:
            status_emoji = "👍"
            status_msg = "Good attempt! Some improvements needed."
        else:
            status_emoji = "⚠️"
            status_msg = "Keep trying! Your code has some issues."
        
        # Create visual progress bars
        def create_bar(percentage):
            filled = int(percentage / 5)
            empty = 20 - filled
            if percentage >= 80:
                color = "🟩"
            elif percentage >= 50:
                color = "🟨"
            else:
                color = "🟥"
            bar = color * filled + "⬜" * empty
            return f"{bar} {percentage}%"
        
        friendly_output = f"""
{status_emoji} **{status_msg}**

### 📊 Your Score Breakdown:

**Overall Reward: {reward:.2f}/1.00** ({reward_percent}%)
{create_bar(reward_percent)}

**Test Results: {test_score:.2f}/1.00** (70% weight)
{create_bar(test_percent)}
{'✓ All tests passed!' if test_percent == 100 else f'✗ Some tests failed - {error_summary[:100] if error_summary else "Check your logic"}'}

**Code Quality: {quality_score:.2f}/1.00** (30% weight)
{create_bar(quality_percent)}
{'✓ Clean code!' if quality_percent >= 80 else '⚠️ Could be cleaner - check style and complexity'}

**Attempt:** {attempt}/{max_attempts}
**Episode Complete:** {'Yes ✓' if done else 'No - You can try again!'}
"""
        
        # Add detailed quality feedback if available
        if quality_feedback and isinstance(quality_feedback, dict):
            try:
                detailed_quality = humanize_quality_feedback(quality_feedback)
                friendly_output += f"\n\n---\n\n{detailed_quality}"
            except Exception:
                pass
        
        technical_output = f"""
**Technical Details:**
- Reward: {reward:.2f}
- Test Score: {test_score:.2f}
- Quality Score: {quality_score:.2f}
- Done: {done}
- Attempt: {attempt}/{max_attempts}

{error_summary if error_summary else "No errors detected."}
        """
        
        return friendly_output, technical_output, ""
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return error_msg, "", ""


def create_interface():
    """Create and return the Gradio interface."""
    # Initialize environment on startup
    initialize_env()
    
    with gr.Blocks(
        title="BugLab - AI Code Debugging",
        css="""
        /* FIXED static height for Your Fix box - matches Problem section exactly */
        .code-wrapper { 
            height: 380px !important; 
            min-height: 380px !important;
            max-height: 380px !important;
            overflow-y: auto !important;
        }
        .code-wrapper .CodeMirror { 
            height: 380px !important;
            min-height: 380px !important;
        }
        .code-wrapper textarea { 
            height: 380px !important;
            min-height: 380px !important;
        }
        .code-wrapper .cm-editor {
            height: 380px !important;
            min-height: 380px !important;
        }
        """
    ) as demo:
        gr.Markdown("""
        # 🐛 BugLab - Debug Python Code with RL
        
        **Fix broken Python code** using a **dual-reward system**: 70% test pass rate + 30% code quality
        """)
        
        # Problem & Code Editing Section (2-column layout)
        with gr.Row():
            with gr.Column(scale=1, min_width=400):
                gr.Markdown("## 📋 Problem")
                problem_description = gr.Textbox(
                    label="Description",
                    lines=4,
                    interactive=False,
                    show_label=True
                )
                problem_status = gr.Textbox(
                    label="Status",
                    interactive=False,
                    show_label=True,
                    lines=2
                )
            
            with gr.Column(scale=1, min_width=400):
                gr.Markdown("## 🔧 Your Fix")
                fixed_code = gr.Code(
                    label="Enter fixed code here",
                    language="python",
                    lines=12,
                    show_label=True,
                    elem_classes="code-wrapper"
                )
        
        # Original Code Section (full width)
        with gr.Row():
            gr.Markdown("## 🐛 Original (Broken) Code")
        
        with gr.Row():
            buggy_code = gr.Code(
                label="",
                language="python",
                interactive=False,
                lines=8,
                show_label=False
            )
        
        # Action Buttons
        with gr.Row(elem_classes="button-row"):
            reset_btn = gr.Button("🔄 Reset Problem", variant="primary", scale=1, size="lg")
            step_btn = gr.Button("▶️ Submit & Evaluate", variant="primary", scale=1, size="lg")
        
        # Results Section
        with gr.Row(elem_classes="results-section"):
            friendly_output = gr.Markdown(
                value="📊 Results will appear here after you submit your fix",
                label=""
            )
        
        # Technical Details (collapsible-like section)
        with gr.Row():
            with gr.Accordion("📈 Technical Details", open=False):
                technical_output = gr.Textbox(
                    label="",
                    interactive=False,
                    lines=8,
                    value="Technical data will appear here...",
                    show_label=False
                )
        
        # Instructions Section
        with gr.Row():
            with gr.Accordion("📖 How to Use & Scoring System", open=False):
                gr.Markdown("""
                ### Quick Start:
                1. Click **🔄 Reset Problem** to load a new debugging task
                2. Read the problem description and study the broken code
                3. Write your fix in the **Your Fix** editor
                4. Click **▶️ Submit & Evaluate** to test your solution
                5. Check your score and detailed feedback below
                
                ### Scoring Breakdown:
                - **70%** - Test Pass Rate: Does your code pass all test cases?
                - **30%** - Code Quality: Is your code clean, efficient, and well-written?
                - **Max Score**: 1.0 (perfect solution)
                
                ### Tips:
                - Read the error summary carefully - it explains what failed
                - You get 3 attempts per problem to fix it
                - Higher difficulty problems earn more reward
                - Focus on correctness first, then optimize for quality
                """)
        
        # Set up event handlers
        reset_btn.click(
            fn=reset_env,
            outputs=[problem_description, buggy_code, problem_status, friendly_output]
        )
        
        step_btn.click(
            fn=step_env,
            inputs=[fixed_code],
            outputs=[friendly_output, technical_output, problem_status]
        )
    
    return demo


if __name__ == "__main__":
    # Create and launch the interface
    # Version 2.2: Detailed Debug Logging for Quality Feedback
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
