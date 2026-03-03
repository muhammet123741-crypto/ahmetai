from agent.core import Agent

if __name__ == "__main__":
    agent = Agent()

    while True:
        user_input = input("Sen: ")
        result = agent.run(user_input)
        print("Asistan:", result)