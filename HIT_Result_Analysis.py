import csv



#-------------------------------------------------------------------------#
#Function: find the major result of the input tweet
def find_major(input):
    result = {}
    for i in input:
        if i not in result.keys():
            result[i] = 1
        else:
            result[i] += 1
    count = 0

    for i in result.values():
        if i == max(list(result.values())):
            count += 1
    if count == 1:
        return max([(value, key) for key, value in result.items()])[1]

    else:
        return 'undecided'

#-------------------------------------------------------------------------#
#Function: Filter out workers with worker_id
def  filter(result, worker_id):
    for i in result.keys():
        del result[i][worker_id]
    return result



#settings
questions_per_HIT = 10
n = 3 #of workers
choice = 4 # of choices
N = 100 # of questions


result = {}
annotation_result = {}
workers = []
workers_list = []
P = []
p = []
p_e = []
tweets = {}
temp_p ={}


#-------------------------------------------------------------------------#
#Loading data, get result for each question and text for each tweet
#tweets = {'id_1': 1, 'id_2',2 ... }
#results = {'id_1':{'worker_id':pos, ...},....}
with open('2993796.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for line in reader:
        for i in range(1, questions_per_HIT+1):#(1,11) = question per HIT
            tweets[line['Input.id'+str(i)]] = line['Input.tweet'+str(i)]
            if line['Input.id' + str(i)] not in result.keys():
                if line['WorkerId'] != 'A2HWLIJP5OVFD5':
                    result[line['Input.id' + str(i)]] = {line['WorkerId']: line['Answer.attitude_' + str(i)]}
                else:
                    result[line['Input.id' + str(i)]] = {'A312KFQ78WB3A4': line['Answer.attitude_' + str(i)]}
            else:
                if line['WorkerId'] != 'A2HWLIJP5OVFD5':
                    result[line['Input.id' + str(i)]].update({line['WorkerId']: line['Answer.attitude_' + str(i)]})
                else:
                    result[line['Input.id' + str(i)]].update({'A312KFQ78WB3A4': line['Answer.attitude_' + str(i)]})



#---------------------------------------#
#filter out worker with low consistency
#result = filter(result, 'ALML8V38FDV0')
#print(result)
#-------------------------------------------------------------------------#
#Calculate Fleiss Kappa
for i in result.keys():
    p_1 = (-1.0) * n
    temp_P = {}# choices
    for i_1 in result[i].keys():
        if result[i][i_1] not in temp_P.keys():
            temp_P[result[i][i_1]] = 1
            if result[i][i_1] not in temp_p.keys():
                temp_p[result[i][i_1]] = 1
            else:
                temp_p[result[i][i_1]] += 1
        else:
            temp_P[result[i][i_1]] += 1
            temp_p[result[i][i_1]] += 1
    for i_3 in temp_P.values():
        p_1 = p_1 + i_3 * i_3
    P.append(p_1/(n*(n-1.0)))
    x = find_major(list(result[i].values()))
    if len(set(result[i].values())) == 1:
        annotation_result[i] = 'unanimous | ' + x
    else:
        if x == 'undecided':
            annotation_result[i] = x + ' | ' + x
            for j in result[i].keys():
                if j not in workers_list:
                    workers_list.append(j)
                    workers.append({j:{i:'outlier'}})
                else:
                    for k in workers:
                        if list(k.keys())[0] == j:
                            k[j].update({i:'outlier'})
        else:
            annotation_result[i] = 'majority | ' + x
            for j in result[i].keys():
                if j not in workers_list:
                    workers_list.append(j)
                    if result[i][j] != x:
                        workers.append({j: {i: 'outlier'}})
                    else:
                        workers.append({j: {i: 'inlier'}})
                else:
                    for k in workers:
                        if list(k.keys())[0] == j:
                            if result[i][j] != x:
                                k[j].update({i: 'outlier'})
                            else:
                                k[j].update({i: 'inlier'})


#-------------------------------------------------------------------------#
#Print and Write to csv file
tweet_result = [['tweet_id', 'decision_type', 'decsiion', 'tweet']] # Header for tweet analysis report
worker_result = [['worker_id','# of outliers', 'consistent percentage']] # Header for worker analysis report
for i in annotation_result.keys():
    tweet_result.append([i, annotation_result[i].split(' | ')[0], annotation_result[i].split(' | ')[1], tweets[i]])
    print(i + ' | ' + annotation_result[i] + ' | ' + tweets[i])
for i in workers:
    t = 0
    for k in i[list(i.keys())[0]].values():
        if k == 'outlier':
            t += 1
    percentage = t * 1.0 / N
    worker_result.append([list(i.keys())[0], t, 1 - percentage])
    print('Worker_Id: ' + list(i.keys())[0] + ' | # of outliers = ' + str(t) + ' | consistent percentage: ' + str(1 - percentage) )

for i in temp_p.values():
    p.append(i/(N*1.0*n))
for i in p:
    p_e.append(i*i)

Fleiss_Kappa = (sum(P)/N - sum(p_e))/(1.0-sum(p_e))
print('Fleiss_Kappa = ' + str(Fleiss_Kappa))

with open('annotation_analysis_report.csv', 'w') as csvfile1:
    spamwriter = csv.writer(csvfile1, delimiter=',')
    for i in tweet_result:
        spamwriter.writerow(i)
with open('worker_analysis_report.csv', 'w') as csvfile2:
    spamwriter1 = csv.writer(csvfile2, delimiter=',')
    for i in worker_result:
        spamwriter1.writerow(i)
    csvfile2.write('Fleiss_Kappa = ' + str(Fleiss_Kappa))