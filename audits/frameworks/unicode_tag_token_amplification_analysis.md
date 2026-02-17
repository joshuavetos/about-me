# Unicode Tag Character Persistence & Token Amplification Analysis  
**Environment:** CPython 3.12+  
**Unicode Range Tested:** U+E0000–U+E007F  
**Date:** 2026  

---

## 1. Objective

Evaluate whether Unicode Tag characters (U+E0000–U+E007F):

1. Survive canonical normalization  
2. Survive JSON round-trip encoding  
3. Remain non-printable at render layer  
4. Inflate token counts across tokenizer architectures  
5. Cause nonlinear token amplification  
6. Reduce effective context window capacity  

This study intentionally avoids vendor-specific system claims and focuses exclusively on encoding-layer behavior.

---

## 2. Normalization & Persistence Results

### Canonical Normalization

All 128 Unicode Tag characters survived:

- NFC  
- NFKC  
- NFD  
- NFKD  

**Result:**  
Canonical and compatibility normalization in CPython 3.12 do not strip Tag characters.

### JSON Round-Trip

All characters survived:

- `json.dumps()`  
- `json.loads()`  

**Result:**  
Standard JSON serialization does not remove these code points.

---

## 3. Visibility & Encoding Characteristics

- All characters are non-printable.  
- Unicode category: `Cf` or `Cn`.  
- UTF-8 byte length: 4 bytes per character.  

This creates measurable divergence between:

- Human-visible string length  
- Byte-level representation  
- Token-level representation  

---

## 4. Tokenizer Differential Study

Tested tokenizers:

- `tiktoken` (cl100k_base BPE)  
- GPT-2 HuggingFace BPE  
- mT5 (SentencePiece)  

### Per-Character Tokenization

| Tokenizer | Mean Tokens per Tag |
|------------|--------------------|
| tiktoken   | ~3                 |
| GPT-2 BPE  | ~4                 |
| mT5 SP     | ~3                 |

These characters are handled as rare byte sequences.  
They are **not special tokens**.  
They do not receive privileged semantic treatment.

---

## 5. Injection Scaling Analysis

Injected increasing counts of Tag characters into:

    INVOICE DATA

Measured token inflation and context impact.

### Observed Pattern

For BPE tokenizers:

- Linear growth.  
- ~3–4 tokens added per injected character.  
- No superlinear scaling observed.  

Example (tiktoken):

| Injected Chars | Token Count | Inflation Multiplier |
|----------------|------------|----------------------|
| 1              | 6          | 2×                   |
| 10             | 33         | 11×                  |
| 100            | 303        | 101×                 |
| 500            | 1503       | 501×                 |

### SentencePiece Behavior

mT5 showed minimal amplification (~1.2×), indicating architecture sensitivity to rare Unicode differs across tokenizer families.

---

## 6. Context Window Impact

Under an 8k context model:

- 500 injected Tag characters consumed ~18–24% of context in BPE tokenizers.  
- SentencePiece models were largely unaffected.  

This represents predictable linear context consumption, not nonlinear collapse.

---

## 7. Sanitization Sensitivity

Tested stripping strategies:

| Strategy                  | Result        |
|---------------------------|--------------|
| Explicit Tag Range Strip  | Stripped     |
| ASCII-Only Filter         | Stripped     |
| XML Clean                 | Stripped     |
| Canonical Normalization   | Survives     |

Conclusion:

Survivability depends on explicit sanitization policy, not normalization.

---

## 8. What This Study Does NOT Demonstrate

This analysis does **not** show:

- Instruction priority elevation  
- Attention hijacking  
- Privilege escalation  
- Agent goal override  
- Real-world exploitability  
- Nonlinear cost explosion  

All observed behavior was:

- Deterministic  
- Linear  
- Encoding-layer predictable  

---

## 9. Core Findings

1. Unicode Tag characters survive canonical normalization in CPython 3.12.  
2. They persist through JSON serialization.  
3. They inflate token counts linearly in BPE tokenizers.  
4. SentencePiece tokenizers are less sensitive.  
5. Context window reduction is proportional and predictable.  
6. No semantic privilege behavior observed.  

---

## 10. Conclusion

Unicode Tag characters represent:

- An encoding-layer persistence phenomenon  
- A linear token amplification behavior in BPE systems  
- A sanitizer-dependent survivability condition  

They do **not** constitute evidence of semantic-layer control, instruction hijack, or backbone compromise within the scope of this study.
