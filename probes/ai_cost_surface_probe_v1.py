import time
import json

n_employees = 15
requests_per_user_per_day = 40
context_length_hint = "4k"

def estimate_tokens(input_hint: str, output_hint: str):
    base_in_factor = {
        "4k": 4000,
        "8k": 8000,
        "16k": 16000,
        "32k": 32000,
    }
    length = base_in_factor.get(input_hint, 1000)
    overhead = length * 0.25
    prompt_toks  = int(length + overhead)
    base_output_toks = 120 + (length // 1000 * 30)
    completion_toks  = int(base_output_toks * 1.10)
    return prompt_toks, completion_toks

all_runs = []

for emp_id in range(n_employees):
    for req_id in range(requests_per_user_per_day):
        p, c = estimate_tokens(context_length_hint, "default")
        total = p + c
        duration = 1.0 + (total / 10000)
        all_runs.append({
            "employee_id": emp_id,
            "request_id": req_id,
            "context_hint": context_length_hint,
            "prompt_tokens": p,
            "completion_tokens": c,
            "total_tokens": total,
            "duration_s": round(duration, 3),
        })

output = {
    "version": "v1.synthetic_anthropic_like_billing",
    "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "n_employees": n_employees,
    "avg_requests_per_user_per_day": requests_per_user_per_day,
    "context_assumption": context_length_hint,
    "total_daily_requests": len(all_runs),
    "total_daily_tokens": sum(r["total_tokens"] for r in all_runs),
    "avg_tokens_per_request": round(sum(r["total_tokens"] for r in all_runs) / len(all_runs), 1),
    "runs": all_runs,
}

print("=== BEGIN COPY‑PASTE OUTPUT TO PERPLEXITY ===")
print(json.dumps(output, indent=2))
print("=== END COPY‑PASTE OUTPUT ===")
