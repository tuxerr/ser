#!/usr/bin/python
# -*- coding: utf-8 -*-

import signal
import sys
import os
import subprocess
import re
import pickle

global gmanager

class Show():
    def __init__(self,name,path):
        self.name=name
        self.current_season=1
        self.current_episode=1
        self.path=path

    def print_status(self):
        print("Show ",self.name," located ",self.path," , currently at S",self.current_season,"E",self.current_episode)

    def goto_path(self):
        os.chdir("/home/"+os.getlogin())
        os.chdir(self.path)

    def goto_currentseason_dir(self):
        self.goto_path()
        l = os.listdir(".")
        acceptable_dirs = [ x for x in l if (re.match(".*[a-zA-Z ]0?"+str(self.current_season)+"(?![0-9])",x)!=None ) ]
        if acceptable_dirs==[]:
            print("Error : Season ",self.current_season," doesn't match any directory in path ",self.path)
            sys.exit()
        else:
            os.chdir(acceptable_dirs[0])
            print("Going to "+acceptable_dirs[0])

    def episode_exists(self,ep_number):
        self.goto_currentseason_dir()
        l = os.listdir(".")
        newlist = [x.replace(str(self.current_season),"~",1) for x in l]
        acceptable_episodes = [ x for x in newlist if (re.match(".*[a-zA-Z ~]0?"+str(ep_number)+"(?![0-9]).*(mkv|avi|wmv|mp4|flv)",x)!=None ) ]
                                
        if acceptable_episodes==[]:
            return False
        else:
            print(acceptable_episodes)
            return acceptable_episodes[0].replace("~",str(self.current_season))


    def play_episode(self):
        global gmanager
        res = self.episode_exists(self.current_episode)
        if res == False:
            print("Show ",self.name," season ",self.current_season," episode ",self.current_episode, "isn't found. Switching to next season")
            self.current_episode=1
            self.current_season+=1
            gmanager.save_data()
            self.play_episode()
        else:
            subprocess.call(["mplayer",res])
            self.current_episode+=1
            gmanager.save_data()
            return self.play_episode()


class Manager():
    def __init__(self):
        self.shows=[]
        os.chdir("/home/"+os.getlogin())
        if os.listdir(".").count(".serdata")==1:
            with open(".serdata","rb") as fileinput:
                self.shows = pickle.load(fileinput)

    def save_data(self):
        os.chdir("/home/"+os.getlogin())        
        with open(".serdata","wb+") as fileoutput:
            pickle.dump(self.shows,fileoutput)

    def __call__(self,signal,frame):
        self.save_data()
        print("Saved modified data in ~/.serdata")
        sys.exit()

    def run(self):
        if len(sys.argv)==1:
            print("List of available shows : ")
            for show in self.shows:
                show.print_status()

        elif sys.argv[1] == "add":
            newshow = Show(sys.argv[2],sys.argv[3])
            self.shows.append(newshow)

        elif sys.argv[1] == "remove":
            for show in self.shows:
                if show.name == sys.argv[2]:
                    self.shows.remove(show)
                    
        elif sys.argv[1] == "play":
            possible=[]
            for show in self.shows:
                if show.name.find(sys.argv[2])==0:
                    possible.append(show)

            if(len(possible)==1):
                possible[0].play_episode()
            else:
                print("Autocomplete fail. Possible shows : ")
                for show in possible:
                    print("    ",show.name)

        elif sys.argv[1] == "status":
            for show in self.shows:
                if show.name == sys.argv[2]:
                    show.print_status()

        elif sys.argv[1] == "set":
            done=False
            for show in self.shows:
                if show.name == sys.argv[2]:
                    show.current_season=int(sys.argv[3])
                    show.current_episode=int(sys.argv[4])
                    done=True

            if done==False:
                print("No show is called ",sys.argv[2])


def main():
    global gmanager
    man = Manager()
    gmanager = man
    signal.signal(signal.SIGINT, man)
    man.run()
    man.save_data()

if __name__ == "__main__":
    main()
