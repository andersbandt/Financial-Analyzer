# Roadmap for Financial-Analyzer Product
written on December 22nd, 2022

## Motivations behind this project

Hello! This is the original creator (Anders). As this project has gotten recent attention and interest I thought I would write my initial motivations behind the project
so newcomers can understand where I was aiming for with this project

My main motivation is to create a **highly customizable** personal financial software. I am **FULLY AWARE** that products like [Mint](https://mint.intuit.com/) exist, 
but after personally trying to use it I was unhappy with the level of customization and analysis capabilities in their product. I also have reservations behind a company having access to a comprehensive list of my personal financial data.

## Various goals to work towards

### Goal - load in spending data and categorize it

This is one aspect of the program that will need some refinement. I would say I have this part *fairly* fleshed out but as people start to play with my current setup
I'm sure issues will be found.

Right now my data is being loaded in through `.csv` files

Currently, each month I go through the following steps...

1. Go to each of my respective accounts and download the account data for that month
2. Place it in the corresponding folder in my financial data file structure
3. Use the software to load it in

I used this process because in the early days of the program I liked to retain the raw data in file format. I am open to this data loading process changing and moving to something like [Plaid](https://plaid.com/), but for now this process has worked just fine.

After data is loaded, the program will try to apply categorization to the transactions. My vision has been to create a highly customizable "category tree", for example
like below

             /-EYECARE
       /HEALTH
      |      \-HYGIENE
      |
      |              /-BARS
      |             |
      |-FOOD AND DRINK-EATING OUT
      |             |
      |              \-RESTAURANT
      |
      |--LIVING
      |
      |-MEDIA-MUSIC
      |
      |-LESIURE-TRAVEL
      |
      |--SHOPPING
      |
      -root       /-TRANSFER
      |-INTERNAL
      |        \-PAYMENT
      |
      |              /-RIDESHARE
      |-TRANSPORTATION
      |              \-GAS
      |
      |      /-INTEREST
      |-INCOME
      |      \-PAYCHECK
      |
      |       /-RENT
      |-HOUSING
      |       \-ENERGY
      |
      |
      |
       \-GIVING


The program will try to apply automatic categorization based on either user set keywords or some other process. **THIS COULD BE A COOL ALGORITHM TO WORK ON**. I can
envision that once the user starts working on it we could have some algorithm to take in past data and info like description, price, even things like day of the week 
to create some algorithm to automatically categorize. 

However, we will also have the option for the user to automatically categorize the data too.


### Goal - analyze spending data, budgeting

Well, what good is loading in the data if you can't analyze it? My vision for this aspect of the program has two parts. The first is to generate very nice data
about spending/income trends (compare it to previous months or something). It would be nice to also have some awesome visualizations on spending.

The second aspect is for the user to create and set a budget. My vision for the budget is that it will all be based on the **category tree**. Basically, the user 
would be able to set budget limits for each category that they create in the tree. For example, in the above tree the user would be able to set a limit of $50 
per month for **RIDESHARE** and $30 per month for **GAS**. They could also set a limit of say $100 for **TRANSPORTATION**, meaning that they will have $20 per month to spend on general **TRANSPORATION** costs (100 - 50 - 30). Obviously there is some details to flesh out there but in a nutshell my vision for the budgeting aspect
is that it will heavily be based on this category tree structure


### Goal - investment tracking

Along with spending/budgeting (which I view as one large section of the program) I have recently (in the past couple days) started to work on investment tracking. My 
broad vision for this is to create **comprehensive portfolio asset tracking**. I really have not touched on this, nor do I have much experience in investment analytics, but enough people seem motivated in this area that I think we could make some progres on this.

To me, the most important concept in investing is [portfolio allocation](https://www.investopedia.com/articles/investing/030116/portfolio-diversification-done-right.asp). How is your money split? Are you in 20% stocks, 60% bonds, and 20% crypto? What is your desired allocation? What adjustments do you need to make 
to get those to where you want to be?

So personally I would like to focus on building a very intuitive way for the user to add personal investment data and then the analytics behind 
producing a comprehensive portfolio split.


## How will we reach this goal? How will work be managed?

I personally have never worked on open source software. I actually have no experience in software collaboration really. I mostly do projects on my own. So I apologize
if this whole project seems disorganized. I am learning as I go along. 

I will do my best to guide and direct as a kind of "project manager" but am also very open to people taking direction on their own - as long as chaos doesn't erupt.

The major immediate action is to create a frontend/backend split away from the tkinter GUI I implemented. It seems like the current plan is to use Vue. I have no 
experience with front end but I will spend some time reading up on it.








