import torch
import torch.optim as optim

import gym
from tensorboardX import SummaryWriter
import copy
import glob
import os
import time
import shutil
import os.path as osp
import stat
from collections import deque
import numpy as np

from algo.twin_sac import TwinSAC
from env import NormalizedContinuousEnv
from argument import get_args
from policies import MLPGuassianPolicy
from policies import UniformPolicy
from networks import QNet
from networks import VNet

from replay_buffer import SimpleReplayBuffer
from logger import Logger

args = get_args()

def experiment(args):
    device = torch.device("cuda:{}".format(args.device) if args.cuda else "cpu")

    env = NormalizedContinuousEnv(gym.make(args.env_name), reward_scale= args.reward_scale)
    env.seed(args.seed)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    if args.cuda:
        torch.backends.cudnn.deterministic=True
    
    pf = MLPGuassianPolicy( env.observation_space.shape[0], env.action_space.shape[0], [args.net, args.net] )
    vf = VNet( env.observation_space.shape[0], [args.net, args.net] )
    qf1 = QNet( env.observation_space.shape[0], env.action_space.shape[0], [args.net, args.net] )
    qf2 = QNet( env.observation_space.shape[0], env.action_space.shape[0], [args.net, args.net] )

    pretrain_policy = UniformPolicy(env.action_space.shape[0])
    
    replay_buffer = SimpleReplayBuffer( args.buffer_size, env.observation_space.shape[0], env.action_space.shape[0] )
    logger = Logger( args.id, args.env_name, args.seed, args.log_dir )

    basic_arguments = {
        'env' : env,
        'replay_buffer' : replay_buffer,
        'logger' : logger,

        'discount' : args.discount,
        'pretrain_frames' : args.pretrain_frames,
        'num_epochs' : args.num_epochs,
        'epoch_frames' : args.epoch_frames,
        'max_episode_frames' : args.max_episode_frames,

        'batch_size' : args.batch_size,
        'min_pool' : args.min_pool,

        'target_hard_update_period' : args.target_hard_update_period,
        'use_soft_update' : args.soft_update,
        'tau' : args.tau,
        'opt_times' : args.opt_times,

        'device' : device,

        'eval_episodes' : args.eval_episodes,
    }

    agent = TwinSAC(
                pf,
                vf,
                qf1 = qf1, qf2 = qf2,
                pretrain_pf = pretrain_policy,

                plr = args.plr,
                vlr = args.vlr,
                qlr = args.qlr,
                
                reparameterization=args.reparameterization,
                automatic_entropy_tuning=args.automatic_entropy_tuning,
                **basic_arguments                
            )
    agent.train()

if __name__ == "__main__":
    # main()
    experiment(args)