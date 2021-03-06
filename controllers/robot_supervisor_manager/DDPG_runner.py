from numpy import convolve, ones, mean, random

# from robot_supervisor_ddpg import PandaRobotSupervisor
from agent.ddpg import DDPGAgent
from robot_supervisor_invRL import PandaRobotSupervisor
import socket
import numpy as np
import pickle
def run():
    # Initialize supervisor object
    env = PandaRobotSupervisor()

    # The agent used here is trained with the DDPG algorithm (https://arxiv.org/abs/1509.02971).
    # We pass (10, ) as numberOfInputs and (7, ) as numberOfOutputs, taken from the gym spaces
    agent = DDPGAgent(alpha=0.000025, beta=0.00025, input_dims=[env.observation_space.shape[0]], tau=0.001, batch_size=64,  layer1_size=400, layer2_size=400, n_actions=env.action_space.shape[0]) 
              
    # agent.load_models() # Load the pretrained model
    episodeCount = 0 
    episodeLimit = 50000
    solved = False  # Whether the solved requirement is met

    # socket
    HOST = '127.0.0.1'
    PORT = 8000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)
    conn, addr = server.accept()
    print(addr)
    # Run outer loop until the episodes limit is reached or the task is solved
    while not solved and episodeCount < episodeLimit:
        state = env.reset()  # Reset robot and get starting observation
        env.episodeScore = 0

        print("===episodeCount:", episodeCount,"===")
        env.target = env.getFromDef("TARGET%s"%(random.randint(1, 10, 1)[0])) # Select one of the targets
        # Inner loop is the episode loop

        for step in range(env.stepsPerEpisode):
            
            # socket
            clientMessage = pickle.loads(conn.recv(1024))
            print('Reward is:', clientMessage)
            print(type(clientMessage))
            message = pickle.dumps(env.CAM.getImageArray())
            serverMessage = message
            conn.send(serverMessage)
            # socket----end
            
            
            # In training mode the agent returns the action plus OU noise for exploration
            act = agent.choose_action(state)

            # Step the supervisor to get the current selectedAction reward, the new state and whether we reached the
            # the done condition
            newState, reward, done, info = env.step(act*0.032)
            # process of negotiation
            while(newState==["StillMoving"]):
                newState, reward, done, info = env.step([-1])
            
            # Save the current state transition in agent's memory
            agent.remember(state, act, reward, newState, int(done))

            env.episodeScore += reward  # Accumulate episode reward
            # Perform a learning step
            if done or step==env.stepsPerEpisode-1:
                # Save the episode's score
                env.episodeScoreList.append(env.episodeScore)
                agent.learn()
                if episodeCount%200==0:
                    agent.save_models()
                solved = env.solved()  # Check whether the task is solved
                break

            state = newState # state for next step is current step's newState
        
        print("Episode #", episodeCount, "score:", env.episodeScore)
        fp = open("Episode-score.txt","a")
        fp.write(str(env.episodeScore)+'\n')
        fp.close()
        episodeCount += 1  # Increment episode counter
    conn.close()
    agent.save_models()
    if not solved:
        print("Reached episode limit and task was not solved, deploying agent for testing...")
    else:
        print("Task is solved, deploying agent for testing...")

    state = env.reset()
    env.episodeScore = 0
    step = 0
    env.target = env.getFromDef("TARGET%s"%(random.randint(1, 10, 1)[0])) # Select one of the targets
    while True:
        act = agent.choose_action_test(state)
        state, reward, done, _ = env.step(act*0.032)
        # process of negotiation
        while(state==["StillMoving"]):
            state, reward, done, info = env.step([-1])
        
        env.episodeScore += reward  # Accumulate episode reward
        step = step + 1
        if done or step==env.stepsPerEpisode-1:
            print("Reward accumulated =", env.episodeScore)
            env.episodeScore = 0
            state = env.reset()
            step = 0
            env.target = env.getFromDef("TARGET%s"%(random.randint(1, 10, 1)[0]))
        
