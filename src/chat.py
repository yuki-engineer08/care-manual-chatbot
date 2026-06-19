import sys

from bot import ask

if sys.stdin.encoding != "utf-8":
    sys.stdin.reconfigure(encoding="utf-8")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    messages = []

    print("介護スタッフ向けチャットボットです。終了するには 'exit' と入力してください。")

    while True:
        user_input = input("\nあなた: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("終了します。")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        assistant_reply = ask(messages)
        messages.append({"role": "assistant", "content": assistant_reply})

        print(f"\nアシスタント: {assistant_reply}")


if __name__ == "__main__":
    main()
