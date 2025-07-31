import matplotlib.pyplot as plt
import io

def create_chart(df, symbol):
    plt.figure(figsize=(10,4))
    plt.plot(df['close'], label="Цена", linewidth=2)
    if 'ema50' in df:
        plt.plot(df['ema50'], label="EMA50", linestyle="--")
    if 'ema200' in df:
        plt.plot(df['ema200'], label="EMA200", linestyle="--")
    plt.title(f"График {symbol}")
    plt.legend()
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf
