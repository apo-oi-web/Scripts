# Voting System 3/15/2019 By Drew Ciccarelli

'''
This voting system program is to run Instant Runoff Voting as noted in
ARTICLE VII: NOMINATIONS AND ELECTIONS
SECTION 3. ELECTIONS

Given a CSV from Qualtrics Rank choice questions
Outputs the winner of the election (first to get 50%+1)

'''

# Updated 11/5/2019 by Daniel McDonough (added comments and edge cases)
# Updated 2/9/2020 by Daniel McDonough (Checked for empty ballots)
# Updated 11/8/2020 by Daniel McDonough (Added Abstain remove check and 50%+2 error)


import pandas as pd
import math



# Read CSV to voting tally
def readCSV(filename):
    df = pd.read_csv(filename)  # read file
    df1 = df.iloc[:, 17:]  # Cut the metadata

    # get the names of Candidates
    names = df1.loc[0,:]
    names = names.str.split('- ', expand=True)[1]

    df1 = df1.rename(columns=names)

    # Cut metadata
    df1 = df1.drop(0)
    VotingMatrix = df1.drop(1)  # matrix of ranks

    # print(VotingMatrix)
    if VotingMatrix.isnull().values.any():
        print("\nThere seem to be some null values! This may happen if a vote was not fully casted! \nMake sure to double check the results just in case! \nRemoving null values...")
        VotingMatrix= VotingMatrix.dropna(axis=0, how='any', thresh=None, subset=None, inplace=False)

    names = names.T.reset_index(drop=True).T  # clean index labels
    keys = names.T.reset_index(drop=True)  # clean index labels
    keys.drop(keys.tail(1).index, inplace=True)

    return VotingMatrix,keys


# Delete Votes that have Abstain as Rank #1
def deleteAbstain(data):
    print("\n\nRemoving Abstention Votes (if any)")

    # Convert data to ints

    data = data.astype(str).astype(int)

    # Remove Votes with Abstain with rank 1
    if 'Abstain' in data:
        data = data[data['Abstain'] > 1]

    # calculate the number of non-abstain votes
    VotesCasted = data.shape[0]  # Get number of total non-abstain votes casted

    if (VotesCasted % 2) == 0:
        Votes_Needed = (VotesCasted / 2) + 1  # Number of votes needed to win
    else:
        Votes_Needed = math.ceil(VotesCasted / 2)  # Number of votes needed to win

    print(str(Votes_Needed) + " (50% + 1) Non Abstention Votes are needed to win\n\n")

    return data, Votes_Needed


# check if a candidate has a count over the 50%+1 required
def checkNumVotes(Votes_needed,counts,names):
    max_val = max(counts)
    max_idx = counts.index(max_val)
    if max_val >= Votes_needed:
        print(names[max_idx] + " has won with " + str(max_val) + " votes")
        exit()


# Recursively Count Votes
def countVotes(data, names, tied_candidates=None, rank=1):

    # Remove all rank 1 abstain votes
    data, Votes_needed = deleteAbstain(data)

    # update ranks to reflect the voters choices once a candidate is removed
    data = IncreaseRanks(data)

    if data.empty:
        print("All votes were Abstain! Re-vote Required")
        exit()

    if not (tied_candidates == None):
        print("Checking Tied votes for candidates: ")
        print(tied_candidates)
        numcandidates = len(tied_candidates)
        counts = [0] * numcandidates  # init empty array to keep track of # 2 Counts
        # for each candidate count the number of votes they got in each "rank"
        for i in range(0, numcandidates):
            votes = data[tied_candidates[i]].value_counts()
            # count the number of Nst picks per candidate (if they exist)
            if rank in votes:
                counts[i] = votes[rank]
    else:
        # print(names.values)
        numcandidates = names.size  # subtract 1 cause we don't account Abstain as a candidate
        counts = [0]*numcandidates  # init empty array to keep track of # 1 Counts

        # for each candidate count the number of votes they got in each "rank"
        for i in range(0,numcandidates):

            votes = data[names[i]].value_counts()

            # count the number of Nst picks per candidate (if they exist)
            if rank in votes:
                counts[i] = votes[rank]

    # Print current ocunt of the votes
    print("Number of "+str(rank)+" choice votes are as follows per candidate:")

    VotesPerCandidate = dict(zip(names.values, counts))
    for k,v in VotesPerCandidate.items():
        print(k+":", v)
    print("\n")

    # check if votes are over 50%+1 if checking 1st rank
    if rank == 1:
        checkNumVotes(Votes_needed,counts,names)



    min_val = min(counts)  # get the count with the lowest 1st pick vote
    min_idx = counts.index(min_val)  # get the index of the smallest count

    # check if there is a tie for last place
    if counts.count(min_val) > 1:
        if rank == numcandidates:
            print("No more ranks to check...")
            if numcandidates == len(names.values):
                print("Re-vote Required...")
                print("ABSOLUTE TIE between candidates: ")
                print(names.values)
                exit()
            else:
                print("Removing all tied candidates...")
                print(tied_candidates)

                for i in tied_candidates:
                    # Note: "No Confidence" is treated like a candidate
                    print("Removing " + i + " from ballot")

                    names_idx = names[names == i].index[0]

                    data.drop(i, axis=1,inplace=True)  # remove the candidate's votes column with lowest score
                    names.drop(names_idx, axis=0,inplace=True)  # remove candidate with lowest score from the list of candidates
                    names = names.T.reset_index(drop=True).T  # clean index labels

                countVotes(data, names)

        else:

            print("WOW, there is a tie for minimum votes! Counting number of "+str(rank+1)+" choice votes")
            min_idx = [i for i, x in enumerate(counts) if x == min_val]
            tied_candidates = [0]*len(min_idx)
            for item in range(len(min_idx)):
                tied_candidates[item] = names[min_idx[item]]
            countVotes(data, names, tied_candidates, rank+1)
    else:
        # lowest vote candidate
        lowest_vote = names[min_idx]

        # Note: "No Confidence" is treated like a candidate
        print("Removing " + lowest_vote + " from ballot")

        data.drop(lowest_vote,axis=1, inplace=True)  # remove the candidate's votes column with lowest score
        names.drop(min_idx, axis=0, inplace=True)  # remove candidate with lowest score from the list of candidates
        names = names.T.reset_index(drop=True).T  # clean index labels



        countVotes(data, names, tied_candidates=None, rank=1)


# BUMP DOWN NUMBERS for all those who chose the removed column
def IncreaseRanks(df):
    # for each row in the dataset
    for index, row in df.iterrows():
        # print(row)  # Ranks with old values EX[2,3,4]

        # sort the candidate by the person's ranked preferences
        copy = row.sort_values()

        newRank = 1  # the highest rank is now ranked 1

        # iterate through the sorted ranks
        for candidate, rank in copy.iteritems():
            df.at[index, candidate] = newRank
            newRank += 1

        # print(row)  # Ranks with new values EX[1,2,3]
    return df


# Final Output:
#  total number votes
#  the rankings


TESTCASES = ['TestCase_All_Abstain.csv', 'TestCase_Last_Place_Tie.csv','TestCase_Absolute_Tie.csv', 'TestCase_Threeway.csv', 'TestCase_Absolute_LastPlace_Tie.csv', 'TestCase_NullValues.csv']

'''
Test Cases Explanations:

    Case TestCase_All_Abstain.csv: 
        Abstain Test: All voters abstain
        Expected Outcome: Complete Re-vote is required
        
    Case TestCase_Last_Place_Tie.csv:
        Last Place Tie: Votes between two candidates are a tie and go to the next rank counts
        Expected Outcome: Gilbert Wins
    
    Case TestCase_Absolute_Tie.csv:
        Last Place Tie: Votes between the last 2 candidates are tied
        Expected Outcome: Re-vote is required between final candidates
        
    Case TestCase_Threeway.csv:
        Last Place Tie: Votes between all 3 candidates are tied
        Expected Outcome: Re-vote is required between all candidates
        
    Case TestCase_Absolute_LastPlace_Tie.csv:
        Last Place Tie: Votes between 2 last place candidates are tied for all ranks
        Expected Outcome: Both last place candidates are removed at the same time, Durtle the Turtle wins
    
    Case TestCase_NullValues.csv:
        Last Place Tie: All Null Value Votes are removed
        Expected Outcome: Both last place candidates are removed at the same time, Durtle the Turtle wins

'''

def main():
    # read the data
    filename = 'Data_Fail2.csv'

    data, keys = readCSV(filename)

    # run the voting code
    countVotes(data, keys)


if __name__ == '__main__':
    main()
