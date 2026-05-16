# AI-assignment

## ⚠️ CRITICAL: Stockfish Engine Configuration

### Step 1: Update Engine Path

In **BOTH** `RandomSensing.py` and `ImprovedAgent.py`, you **MUST** update the Stockfish engine path to match your system.

**🔍 Find this line (around line 18):**
```python
self.engine = chess.engine.SimpleEngine.popen_uci(r'C:\Users\mbaye\Downloads\Assignment\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe')
```

**✏️ Change it to YOUR Stockfish location:**
