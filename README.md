GPT2 bot that runs on discord.py 2.1, Also capable of training data files if needed. 

Install at your own risk. Tensor, pytorch, etc can all be really finnicky between OS/deployments. 

The current requirements.txt file worked on my debian based server for cpu-only tasks. I have also successfully managed to get Training working on windows with the cuda developer packages installed along with a conda deployment cuda installed along with tensor. I have uploaded my conda package list, I don't recommend installing all of them but it may help with troubleshooting any issues running training/the bot on gpu. 

All important values can be found in config.ini. You can name the config anything you'd like but I'd recommend keeping the config.ini file in the directory as a fallback, but additional configs can be loaded using the --config [name of file without the extension (ex: config for config.ini)].

Below are the rest of the switches currently implemented:



**arg**|**info**
:---------:|-----
**--clean**|Clean a **rawtext.txt** file discord chatlog into something with less junk data
**--config**|Specifies a custom config file. Defaults to **config.ini** if not specified. argument should be just the file name, no extension.
**--data**|Set a non default datafile to train on.
**--encode**|Encode a dataset into a compressed archive.
**--model**|Specify a custom folder to use a training model from. Defaults to **"trained_model"** if not specified
**--togpu**|By default this is set to 0 in the config so it loads as false later on. Enabling this flag will have this flag as **"True"**
**--train**|Trains the model on a file named **dataset_cache.tar.gz**
**--test**|Test model by talking to the AI right in the terminal.
