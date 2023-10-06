# mario kart ai
implementation of [1604.07316](https://arxiv.org/abs/1604.07317). meant to be taught as an small 3 day class system at itesm.

**status: ** the repo is on a stage of logging succesfully the data necesary, model development and testing is what follows.

(repo name is tensorgba because it could work with any other game)

## todo
- [X] send filepath to save screenshots from python -> lua
    - [X] textinput, always send this string as folder inside of original data folder sent first
- [X] implement logging to csv file
    - [X] data folder
        - [X] several folders inside with pictures and data
- [X] picture visualization
- [X] convert csv to npy
- [X] train model
    - [X] test controllers are registered in log window
- [ ] update requirements.txt for all files
- [ ] implement logic of receiving inputs in lua
- [X] test model
- [ ] work on ppts
    -[ ] diagrams
- [ ] add instructions in how to run

# ideas for improvement
- [ ] better gameplay
- [ ] YUV instead of RGB
- [ ] smoothing images
