import time
import json

n_employees = 15
requests_per_user_per_day = 40
team_runs_per_day = n_employees * requests_per_user_per_day
TOOL_BASE_OVH = 346
SIMPLE_TOOL_LEN = 100
tool_setup_ovh = TOOL_BASE_OVH + 2 * SIMPLE_TOOL_LEN

context_configs = [
    ("4k_std", 4000, False),
    ("4k_tools", 4000, False),
    ("32k_std", 32000, True),
    ("200k_std", 200000, False),
]

models = [
    ("claude-4.5-haiku",   1.0,  5.0,  1.25, 0.10),
    ("claude-4.5-sonnet",  3.0, 15.0,  3.75, 0.30),
    ("claude-4.5-opus",    5.0, 25.0,  6.25, 0.50),
]

all_scenarios = []

def cost_per_million(p_per_m):
    return p_per_m / 1_000_000

for model_cfg in models:
    model_name, in_price_m, out_price_m, cache_write_p, cache_read_p = model_cfg
    cache_hit_ratio = 0.70

    for ctx_name, base_in_toks, is_long in context_configs:
        input_base = base_in_toks
        if "tools" in ctx_name:
            overhead = tool_setup_ovh
        else:
            overhead = 200
        input_toks = input_base + overhead
        output_toks = 264
        total_toks = input_toks + output_toks

        cached_input = int(input_toks * cache_hit_ratio)
        uncached_input = input_toks - cached_input

        if is_long and input_toks > 200_000:
            in_price_m_eff = in_price_m * 2
            out_price_m_eff = out_price_m * 1.5
        else:
            in_price_m_eff = in_price_m
            out_price_m_eff = out_price_m

        in_cost_p = cost_per_million(in_price_m_eff)
        out_cost_p = cost_per_million(out_price_m_eff)
        cache_write_p_t = cost_per_million(cache_write_p)
        cache_read_p_t = cost_per_million(cache_read_p)

        per_call_cost = (
            uncached_input * in_cost_p +
            cached_input   * cache_write_p_t +
            cached_input   * cache_read_p_t +
            output_toks    * out_cost_p
        )

        effective_in_cost = (
            (uncached_input * in_cost_p + cached_input * cache_write_p_t) / input_toks
            if input_toks > 0 else 0
        )
        effective_out_cost = (
            output_toks * out_cost_p / output_toks
            if output_toks > 0 else 0
        )

        daily_calls = team_runs_per_day
        daily_cost = daily_calls * per_call_cost
        monthly_cost = daily_cost * 30

        daily_total_tokens = daily_calls * total_toks

        roster = [
            {
                "employee_id": emp,
                "request_id": req,
                "input_tokens": input_toks,
                "output_tokens": output_toks,
                "tool_overhead_tokens": overhead if "tools" in ctx_name else 0,
            }
            for emp in range(n_employees)
            for req in range(requests_per_user_per_day)
        ]

        scenario = {
            "model": model_name,
            "pricing_context": ctx_name,
            "is_long_context": is_long,
            "input_price_usd_per_million": in_price_m_eff,
            "output_price_usd_per_million": out_price_m_eff,
            "prompt_cache_write_price_usd_per_million": cache_write_p,
            "prompt_cache_read_price_usd_per_million": cache_read_p,
            "per_request_input_tokens": int(input_toks),
            "per_request_output_tokens": int(output_toks),
            "per_request_total_tokens": int(total_toks),
            "per_request_tool_overhead_tokens": tool_setup_ovh if "tools" in ctx_name else None,
            "per_request_cost_usd": per_call_cost,
            "effective_per_token_in_cost_usd": effective_in_cost,
            "effective_per_token_out_cost_usd": effective_out_cost,
            "n_employees": n_employees,
            "requests_per_user_per_day": requests_per_user_per_day,
            "daily_total_calls": daily_calls,
            "daily_total_tokens": daily_total_tokens,
            "daily_cost_usd": daily_cost,
            "monthly_cost_usd": monthly_cost,
            "roster": roster,
        }
        all_scenarios.append(scenario)

output = {
    "version": "v2.enterprise_billing_foreign_model",
    "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "config": {
        "n_employees": n_employees,
        "requests_per_user_per_day": requests_per_user_per_day,
        "team_daily_requests": team_runs_per_day,
        "cache_hit_ratio_assumption": cache_hit_ratio,
        "tool_setup_overhead": tool_setup_ovh,
    },
    "scenarios": all_scenarios,
}

print("=== BEGIN COPY‑PASTE OUTPUT TO PERPLEXITY ===")
print(json.dumps(output, indent=2))
print("=== END COPY‑PASTE OUTPUT ===")
