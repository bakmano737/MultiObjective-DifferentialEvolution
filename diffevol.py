##########################
# diffevol.py            #
# Differential Evolution #
#   by James V. Soukup   #
#   for CEE 290 HW #4    #
##########################
##################################################
# The models and cost functions are in models.py #
##################################################
import numpy as np
from numpy import random as rnd

######################################################################
# Differential Evolution                                             #
######################################################################
#  Recombination:                                                    #
#    child = parent + fde*(mate1-mate2)                              #
#    mate1 - First randomly selected member of the population        #
#    mate2 - Second randomly selected member of the population       #
#  Parameters:                                                       #
#    Pop    - Initial population of parameters                       #
#    cost   - Costs of initial population                            #
#    cr     - Crossover probability                                  #
#    fde    - Child variability factor                               #
#    pmut   - Mutation Probability                                   #
#    i      - Generation counter                                     #
#    im     - Max Generation Count                                   #
#    etol   - Exit Tolerance (Convergance)                           #
#    hist   - Lowest SSR of all previous generations (Analysis)      #
#    cf     - Cost Function                                          #
#    carg   - Cost Function Arguments                                #
######################################################################
def diffevol(Pop,cost,cr,fde,pmut,i,im,hist,etol,cf,carg):
    #########################
    # Step One: Selection   #
    #########################
    # Generate two unique random integers #
    # for each member of the population   #
    r = rnd.choice(Pop[:,0].size, (Pop[:,0].size,2))
    # Replace pairs of duplicates with a unique pair
    dup    = r[:,0]==r[:,1]
    r[dup] = rnd.choice(Pop[:,0].size,r[dup].shape,False)
    # Define the mating partners
    FirstMates = Pop[r[:,0],:]
    SecndMates = Pop[r[:,1],:]
    ####################
    # Step Two: Mating #
    ####################
    # Partial Crossover
    Pcr = rnd.choice([0,1],Pop.shape,p=[1-cr,cr])
    # Recombination
    mateDiff = np.subtract(FirstMates,SecndMates)
    crssover = np.multiply(fde*Pcr,mateDiff)
    Child    = np.mod(np.add(Pop,crssover),1)
    # Mutation
    Mut = rnd.rand(*Child.shape)
    Mut = Mut<pmut
    Child[Mut] = rnd.rand(*Child[Mut].shape)
    #########################
    # Step Three: Rejection #
    #########################
    # Evaluate Cost for Child Population
    chCst = cf(Child,carg)
    costc = chCst[1][1]
    costp = cost[1][1]
    # Replace dominated offspring with parent
    dom = np.array(np.greater(costc,costp)).reshape((-1,))
    Child[dom] = Pop[dom]
    np.minimum(costc,costp,out=costc)
    chCst[1][1] = costc

    # Best in show
    best = np.min(costc)
    hist[i] = best

    # Check convergance
    #if best <= etol:
    #   return [Child,chCst]

    # Check Generation Counter 
    if (im <= i+1):
        # Maximum Number of generations reached
        # Return the current population
        return [Child,chCst]

    ##############################
    # Create the next generation #
    ##############################
    return diffevol(Child,chCst,cr,fde,pmut,i+1,im,hist,etol,cf,carg)

######################################################################
# Differential Evolution Alternate Recombination                     #
######################################################################
#  Recombination:                                                    #
#    child = parent + fde*(mate1-mate2) + lam*(best-parent)          #
#    best  - Individual with lowest SSR in current generation        #
#    mate1 - First randomly selected member of the population        #
#    mate2 - Second randomly selected member of the population       #
#  Parameters:                                                       #
#    Pop   - Initial population of parameters                        #
#    cost  - Costs of initial population                             #
#    cr    - Crossover probability                                   #
#    fde   - Child variability factor                                #
#    lam   - Best parent scaling factor                              #
#    pmut  - Mutation Probability                                    #
#    i     - Generation counter                                      #
#    im    - Max Generation Count                                    #
#    etol  - Exit Tolerance (Convergance)                            #
#    hist  - Lowest SSR of all previous generations (Analysis)       #
#    cf    - Cost Function                                           #
#    carg  - Cost Function Arguments                                 #
######################################################################
def dealt(Pop,cost,cr,fde,lam,pmut,i,im,hist,etol,cf,carg):
    #########################
    # Step One: Selection   #
    #########################
    # Generate two unique random integers #
    # for each member of the population   #
    r = rnd.choice(Pop[:,0].size, (Pop[:,0].size,2))
    # Replace pairs of duplicates with a unique pair
    dup    = r[:,0]==r[:,1]
    r[dup] = rnd.choice(Pop[:,0].size,r[dup].shape,False)
    # Define the mating partners
    FirstMates = Pop[r[:,0],:]
    SecndMates = Pop[r[:,1],:]
    # Best in show
    besti = np.argmin(cost[1][1])
    bestp = Pop[besti,:]
    hist[i] = cost[1][1][besti]

    ####################
    # Step Two: Mating #
    ####################
    # Partial Crossover
    Pcr = rnd.choice([0,1],Pop.shape,p=[1-cr,cr])
    # Recombination
    mateDiff = np.subtract(FirstMates,SecndMates)
    bestDiff = np.subtract(bestp,Pop)
    crssover = np.multiply(fde*Pcr,mateDiff)
    bestover = np.multiply(lam*Pcr,bestDiff)
    fullover = np.add(crssover,bestover)
    Child    = np.mod(np.add(Pop,fullover),1)
    # Mutation
    Mut = rnd.rand(*Child.shape)
    Mut = Mut<pmut
    Child[Mut] = rnd.rand(*Child[Mut].shape)
    #########################
    # Step Three: Rejection #
    #########################
    # Evaluate Cost for Child Population
    chCst = cf(Child,carg)
    costc = chCst[1][1]
    costp = cost[1][1]
    # Replace dominated offspring with parent
    dom = np.array(np.greater(costc,costp)).reshape((-1,))
    Child[dom] = Pop[dom]
    np.minimum(costc,costp,out=costc)
    chCst[1][1] = costc

    # Check convergance
    #if best <= etol:
    #   return [Child,chCst]

    # Check Generation Counter 
    if (im <= i+1):
        # Maximum Number of generations reached
        # Return the current population
        return [Child,chCst]

    ##############################
    # Create the next generation #
    ##############################
    return dealt(Child,chCst,cr,fde,lam,pmut,i+1,im,hist,etol,cf,carg)

######################################################################
# Differential Evolution Multi Objective Pareto Ranking              #
######################################################################
#  Recombination:                                                    #
#  Parameters:                                                       #
#    Pop   - Initial population of parameters                        #
#    cost  - Costs of initial population                             #
#    cr    - Crossover probability                                   #
#    fde   - Child variability factor                                #
#    lam   - Best parent scaling factor                              #
#    pmut  - Mutation Probability                                    #
#    i     - Generation counter                                      #
#    im    - Max Generation Count                                    #
#    etol  - Exit Tolerance (Convergance)                            #
#    hist  - Lowest SSR of all previous generations (Analysis)       #
#    cfs   - Cost Function                                           #
#    cargs - Cost Function Arguments                                 #
######################################################################
def demo(Pop,Cost,cr,fde,pmut,i,im,cf):
    #########################
    # Step One: Selection   #
    #########################
    # Generate two unique random integers #
    # for each member of the population   #
    N = Pop.shape[0]
    r = rnd.choice(N, (N,2))
    # Replace pairs of duplicates with a unique pair
    dup    = r[:,0]==r[:,1]
    r[dup] = rnd.choice(N,r[dup].shape,False)
    # Neither element of r can be its own index
    a = np.arange(N).reshape((N,1))
    r[np.equal(r,a)] = np.mod(r[np.equal(r,a)]+1,N)
    # Define the mating partners
    FirstMates = Pop[r[:,0],:]
    SecndMates = Pop[r[:,1],:]

    ####################
    # Step Two: Mating #
    ####################
    # Partial Crossover
    Pcr = rnd.choice([0,1],Pop.shape,p=[1-cr,cr])
    # Recombination
    mateDiff = np.subtract(FirstMates,SecndMates)
    crssover = np.multiply(fde*Pcr,mateDiff)
    Child    = np.mod(np.add(Pop,crssover),1)
    # Mutation
    Mut = rnd.rand(*Child.shape)
    Mut = Mut<pmut
    Child[Mut] = rnd.rand(*Child[Mut].shape)

    #########################
    # Step Three: Rejection #
    #########################
    # Evaluate Cost for Child Population
    ChCst = cf(Child)
    # Pareto Ranking
    TP = np.vstack((Pop, Child))
    TC = np.vstack((Cost,ChCst))
    Unranked = np.hstack((TP,TC))
    Ranked = np.array([[],[],[]]).T
    rankPop(Unranked,Ranked,Pop.size)
    Child = TP[Ranked[0]]
    ChCst = Ranked[1]

    # Check Generation Counter 
    if (im <= i+1):
        # Maximum Number of generations reached
        # Return the rank1 population and cost
        return rank1([Child,ChCst])

    ##############################
    # Create the next generation #
    ##############################
    return demo(Child,ChCst,cr,fde,pmut,i+1,im,cf)

def rankPop(Unranked,Ranked,stop):
    uPop = Unranked[:,0]
    uPop = np.reshape(uPop,(uPop.size,1))
    uCst = Unranked[:,1:]
    rPop = Ranked[:,0]
    rCst = Ranked[:,1:]
    # Choose a random individual from unranked pop
    ind = np.mod(rnd.randint(0,uPop.shape[0]),uPop.shape[0])
    # Determine the individuals who dominate the chosen one
    # ALL of their costs are LESS than or EQUAL to the chosen one
    Dms = np.all(np.less_equal(uCst,uCst[ind,:]),axis=1)
    if np.any(Dms):
        # Rank the dominating population
        unr = np.hstack((uPop[Dms],uCst[Dms]))
        rankPop(unr,Ranked,stop)
    else:
        # Chosen individual is rank 1
        # Add the individual to the ranked population
        rPop.append(uPop[ind,:])
        rCst.append(uCst[ind,:])
        Ranked.append(np.hstack(rPop,rCst)) 
        # Check to see if the desired final population is reached
        if len(rPop) >= stop:
            return
        else:
            # If there is need to continue, remove the individual
            # from the unranked population and rank the new
            # unranked population
            np.delete(uPop,ind,axis=0)
            np.delete(uCst,ind,axis=0)
            unr = np.hstack((uPop,uCst))
            rankPop(unr,Ranked,stop)
    return

def rank1(Pop):
    # Return all Rank 1 solution in the given population
    pars = Pop[0]
    csts = Pop[1]
    rk1p = []
    rk1c = []
    for i in range(len(pars)):
        if len(~np.any(np.less(csts[i],csts),axis=1)):
            # i is not rank 1
            continue
        else:
            # i is rank 1
            rk1p.append(pars[i])
            rk1c.append(csts[i])
    return [rk1p,rk1c]