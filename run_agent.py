from agent.graph import create_agent_graph
from langchain_core.messages import HumanMessage

def main():
    # Build the graph with default tools and LLM
    graph = create_agent_graph()
    # Prepare the initial state: a single human message asking a question
    input_state = {"messages": [HumanMessage(content="What is my CGPA?")]}
    # Run the graph to completion
    result = graph.invoke(input_state, config={"configurable": {"thread_id": "run_agent_1"}})
    print("--- Agent result ---")
    print(result)

if __name__ == "__main__":
    main()
