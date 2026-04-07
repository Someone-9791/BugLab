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
        
        # DEBUG: Log what we're getting
        print(f"[DEBUG] step_env() results:", flush=True)
        print(f"  quality_feedback type: {type(quality_feedback)}", flush=True)
        print(f"  quality_feedback is None: {quality_feedback is None}", flush=True)
        print(f"  quality_feedback bool: {bool(quality_feedback)}", flush=True)
        if quality_feedback:
            print(f"  quality_feedback keys: {list(quality_feedback.keys())}", flush=True)
        print(f"  quality_score: {quality_score}", flush=True)
        print(f"  test_score: {test_score}", flush=True)
        print(f"  reward: {reward}", flush=True)
        
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
        # Add visible debug info to help diagnose
        friendly_output += f"\n\n**[DEBUG] quality_feedback status:**\n"
        friendly_output += f"- Type: {type(quality_feedback).__name__}\n"
        friendly_output += f"- Is None: {quality_feedback is None}\n"
        friendly_output += f"- Is dict: {isinstance(quality_feedback, dict)}\n"
        
        print(f"[DEBUG] Checking quality_feedback for humanization:", flush=True)
        print(f"  quality_feedback: {quality_feedback}", flush=True)
        print(f"  type check: {isinstance(quality_feedback, dict)}", flush=True)
        
        if quality_feedback and isinstance(quality_feedback, dict):
            print(f"[DEBUG] quality_feedback is valid dict, calling humanize_quality_feedback()", flush=True)
            try:
                detailed_quality = humanize_quality_feedback(quality_feedback)
                friendly_output += f"\n\n---\n\n{detailed_quality}"
                print(f"[DEBUG] Successfully added humanized feedback", flush=True)
            except Exception as hum_err:
                print(f"[DEBUG] ERROR humanizing: {hum_err}", flush=True)
                import traceback
                friendly_output += f"\n\n---\n\n**[ERROR] Rendering quality feedback failed:**\n```\n{traceback.format_exc()}\n```"
        else:
            print(f"[DEBUG] Skipping quality feedback - not a dict or empty", flush=True)
            if quality_feedback:
                friendly_output += f"\n- Content sample: {str(quality_feedback)[:100]}\n"
        
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
        print(f"[DEBUG] Exception in step_env: {error_msg}", flush=True)
        return error_msg, "", ""


def create_interface():
    """Create and return the Gradio interface."""
    # Initialize environment on startup
    initialize_env()
    
    with gr.Blocks(title="BugLab - AI Code Debugging") as demo:
        gr.Markdown("""
        # 🐛 BugLab - Debug Python Code with RL
        
        An environment where AI agents fix broken Python code using a dual-reward system:
        - **70%**: Test pass rate (deterministic)
        - **30%**: Code quality score (deterministic static analysis)
        
        Try debugging code problems below!
        """)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Problem")
                problem_description = gr.Textbox(
                    label="Problem Description",
                    lines=3,
                    interactive=False
                )
                
                gr.Markdown("### Buggy Code")
                buggy_code = gr.Code(
                    label="Original (Broken) Code",
                    language="python",
                    interactive=False
                )
            
            with gr.Column():
                gr.Markdown("### Your Fix")
                fixed_code = gr.Code(
                    label="Fixed Code",
                    language="python",
                    lines=10
                )
        
        with gr.Row():
            reset_btn = gr.Button("🔄 Reset (Get New Problem)", variant="primary", scale=1)
            step_btn = gr.Button("▶️ Submit Fix & Get Reward", variant="primary", scale=1)
        
        with gr.Row():
            with gr.Column(scale=2):
                friendly_output = gr.Markdown(
                    label="Your Results",
                    value="Submit your fix to see results here!"
                )
            with gr.Column(scale=1):
                technical_output = gr.Textbox(
                    label="Technical Details",
                    interactive=False,
                    lines=10,
                    value="Technical details will appear here..."
                )
        
        problem_status = gr.Textbox(
            label="Problem Status",
            interactive=False
        )
        
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
        
        gr.Markdown("""
        ---
        
        ## 📖 How to Use:
        1. Click **🔄 Reset** to get a new debugging problem
        2. Read the problem description and examine the broken code
        3. Write your fixed code in the **Your Fix** section
        4. Click **▶️ Submit Fix** to evaluate your solution
        5. Review your **visual score breakdown** and **technical details**
        
        ### 🎯 Scoring System:
        - **70%** from test pass rate (did your code pass the tests?)
        - **30%** from code quality (is your code clean and well-written?)
        - **Maximum reward:** 1.0 (perfect score)
        
        💡 **Tip:** Read the error summary if tests fail - it tells you exactly what went wrong!
        """)
    
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
