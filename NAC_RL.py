import requests
import fpdf #sudo pip install fpdf (sudo yum install python-pip)

def get_results_file(eventid):
    # look in cache for a results file, if not there, create it and fill from web
    filename = eventid + '.txt'
    try:
        filename = eventid + '.txt'
        res_file = open(filename,'r')
        res_text = res_file.read()
        #print(res_text[:100])
        res_file.close()
        print('Results website already stored in local cache')
        return filename
    except:
        res_file = open(filename,'a')
        base_url = "https://www.runbritainrankings.com/results/results.aspx"
        ii = 1
        while ii in range(10):
            params_dict = {"meetingid":eventid,"pagenum":ii}
            res_page = requests.get(base_url,params=params_dict)
            if "No results found" not in res_page.text:
                print(res_page.url)
                res_file.write(res_page.text.encode('utf-8').strip())
                #print(res_page.url)
                ii += 1
            else:
                print('Found {} results pages online'.format(ii-1))
                ii = 100
        res_file.close()
        return filename

def get_event_results(all_events_list):
    # for all events, look through the results file, find NAC athletes and store their performance data
    event_dict = {}
    for event in all_events_list:
        event_name = event.get('Name')
        event_id = event.get('WebID')
        print('Looking up {}\n'.format(event_name))
        results_file = get_results_file(event_id)
        event_file = open(results_file,'r')
        ii = 0
        res_list = []
        res_dict = {}
        line_list = []
        event_dict[event_name] = []
        for line in event_file:
            if ('Newbury' in line) and ('Newbury Runners' not in line) and ("athleteid" in line): # and ("Green" in line):
                res_dict = {}
                line_list = line.split('</td>')
                for el in range(len(line_list)):
# find the runner name
                    if 'athleteid' in line_list[el]:
                        res_dict['Name'] = line_list[el].split('</a>')[0].split('>')[-1]
                    if 'Newbury' in line_list[el]:
# find their gender
                        res_dict['Gender']=line_list[el-1].split('>')[1]
# find their age category
                        el_list = line_list[el-2].split('>')
                        if 'S' in el_list[1]:
                            ag = 'SEN'
                        elif 'V' in el_list[1]:
                            if int(el_list[1][1:]) >= 50:
                                ag = 'VET'
                            else:
                                ag = 'SEN'
                        else:
                            ag = 'U18'
                        res_dict['AgeCat']=ag
# find the runner position
                res_dict['position'] = int(line_list[1].split('>')[1])
# is this a PB?
                res_dict['PB'] = str(['YES' if 'PB' in line else 'NO'][0])
# create space to store points
                res_dict['Points']=0
# increase counter
                ii += 1
                print(ii,res_dict)
                event_dict[event_name] += [res_dict]
        print('found {} Newbury athletes in {}\n'.format(ii,event_name))
    return event_dict

def get_athletes(nEvents,events_res_dict,Gen,Age):
    # define a list of athletes in an Age and Gender category
    aths = []
    for ii in events_res_dict.keys():
        for athlete in events_results_dict.get(ii):
            if (athlete.get('Gender')==Gen) and (athlete.get('AgeCat')==Age):
                add = True
                for aa in aths:
                   if (athlete.get('Name')==aa.keys()[0]):
                       add = False
                if add:
                    ath = {}
                    ath[athlete.get('Name')] = []
                    for jj in range(nEvents+2):
                        ath[athlete.get('Name')] += [0]
                    aths += [ath]
    return aths

def get_event_points_by_group(ath_list,event_res_dict):
    pts = 20
    res = []
    for ath in ath_list:
        for ii in range(len(event_res_dict)):
            if ath.keys()[0]==event_res_dict[ii].get('Name'):
                res += [event_res_dict[ii]]
    res = sorted(res,key=lambda k:k.get('position'))
    for ath in res:
        for ii in range(len(event_res_dict)):
            if ath.get('Name')==event_res_dict[ii].get('Name'):
                event_res_dict[ii]['Points'] = pts
                if pts>1:
                    pts -= 1
    return event_res_dict

def print_events_dict(events_results_dict):
    for event in events_results_dict:
        for ath in events_results_dict.get(event):
            print(ath)
        print('---')

def assign_athlete_points_by_event(ID,ath_group,list_of_event_ath_dicts):
    for ath in ath_group:
        points = ath.values()[0]
        for event_ath in list_of_event_ath_dicts:
            if ath.keys()[0]==event_ath.get('Name'):
# assign event points
                points[ID] = event_ath.get('Points')
# add a PB if valid
                if event_ath.get('PB')=='YES' and points[0]<3:
                    points[0] += 1
    return ath_group

def update_athlete_totals(nEvents,ath_group):
    for ath in ath_group:
        points = ath.values()[0]
        points[nEvents+1] = 0
        for ii in range(nEvents):
            points[nEvents+1] += points[ii+1]
        points[nEvents+1] += points[0]*3
        ath.values()[0] = points
    return ath_group

def get_max_name_len(group_name,athlete_group,nEvents):
    max_gname_len = 0
    for ath in athlete_group:
        max_gname_len = max(max_gname_len,len(ath.keys()[0]))
    return max_gname_len

def write_results_table(max_name_len,group_name,athlete_group,nEvents,pdf):
    print(group_name)
    pdf.cell(0, 4.5, txt=group_name, ln=1, align="L")
    max_rank_len = 4
    max_pts_len = 3
    
    eventIDs = []
    for ii in range(nEvents):
        if (ii+1)<10:
            eventIDs += ['  '+str(ii+1)]
        else:
            eventIDs += [' '+str(ii+1)]
    title = 'Rank | Name{} |{} | PBs | Total'.format(' '*(max_name_len-4),''.join(eventIDs))
    print(title)
    print('-'*len(title))
    pdf.cell(0, 4.5, txt=title, ln=1, align="L")
    pdf.cell(0, 4.5, txt='-'*len(title), ln=1, align="L")
    ranked_athletes = sorted(athlete_group,key=lambda k: (k.values()[0][nEvents+1],k.values()[0][0]),reverse=True)
    rank = 1
    prev_tot_score = -1
    for r_ath in ranked_athletes:
        if r_ath.values()[0][nEvents+1]==prev_tot_score:
            rank_str = '='
        else:
            rank_str = str(rank)
        prev_tot_score = r_ath.values()[0][nEvents+1]
        rank_space = max_rank_len - len(rank_str)-1
        name_space = max_name_len - len(r_ath.keys()[0])
        points = []
        for ii in range(nEvents):
            a_point = str(r_ath.values()[0][ii+1])
            pts_space = max_pts_len - len(a_point)
            points += [' '*pts_space + a_point]
        print('{}{}  | {}{} |{} |  {}  | {}'.format(' '*rank_space,rank_str,r_ath.keys()[0],' '*name_space,''.join(points),r_ath.values()[0][0]*3,r_ath.values()[0][nEvents+1]))
        pdf.cell(0, 4.5, txt='{}{}  | {}{} |{} |  {}  | {}'.format(' '*rank_space,rank_str,r_ath.keys()[0],' '*name_space,''.join(points),r_ath.values()[0][0]*3,r_ath.values()[0][nEvents+1]), ln=1, align="L")
        rank += 1

    print('\n')
    pdf.cell(0, 4.5, txt=' ', ln=1, align="L")

    return

def get_events_list():
    filename = 'events.txt'

    elist = []
    ev_types = {}
    ev_types['5 km']='parkrun'
    ev_types['10 km']='10K'
    ev_types['5 miles']='5M'
    ev_types['5 mile']='5M'
    ev_types['10 miles']='10M'
    ev_types['10 mile']='10M'
    ev_types['half marathon']='HM'
    ev_types['20 miles']='20M'
    ev_types['20 mile']='20M'

#    try:
    with open(filename) as ev_file:
        id = 0
        for line in ev_file:
            id += 1
            ev_text = line
            ev_dict = {}
            details = ev_text.split(',')
            for ii in range(len(details)):
                el = details[ii]
                el = el.replace('\t','')
                el = el.replace('\n','')
                el = el.strip()
                details[ii] = el
            ev_dict['ID'] = id
            ev_dict['Name'] = details[2]
            date_list = details[0].split(' ')
            day = date_list[0]
            day = day.replace('th','')
            day = day.replace('rd','')
            day = day.replace('nd','')
            day = day.replace('st','')
            date_list[0] = day
            month = date_list[1][0:3]
            date_list[1] = month
            ev_dict['Date']='-'.join(date_list)
            ev_dict['Type']=ev_types.get(details[1].lower())
            pb='YES'
            if ev_dict['Type']==None:
                pb='NO'
            ev_dict['PBable']=pb
            ev_dict['Venue']=details[3]
            #print(ev_dict)
            param_dict = {}
            param_dict['terraintypecodes']='A'
            if ev_dict['Type']!=None:
                param_dict['event']=ev_dict.get('Type')
            param_dict['datefrom']=ev_dict.get('Date')
            param_dict['dateto']=ev_dict.get('Date')
            param_dict['venue']=ev_dict.get('Venue')
            base_url = 'https://www.thepowerof10.info/results/resultslookup.aspx?'
            ev_page = requests.get(base_url,params=param_dict)
            page_list = ev_page.text.split('\n')
            print(ev_page.url)
#            print(page_list)
#            print('~~~')
            id_str = []
            for line in page_list:
                if 'meetingid' in line:
                    id_list = line.split('meetingid')
#                    for el in id_list:
#                        print(el)
                    id_str = id_list[1]
#                    print(id_str)
                    id_list = []
                    id_list = id_str.split('>')
                    id_str = id_list[0]
                    id_str = id_str.replace('=','')
                    id_str = id_str.replace('"','')
#                    for el in id_list:
#                        print(el)
#                    print(id_list)
#            print('~~~')
#            print(ev_page.url)
#            print(param_dict)
            ev_dict['WebID'] = str(id_str)
#            print(ev_dict)
            elist += [ev_dict]
        return elist
#    except:
#        print("Error: Couldn't open events file.")
#        return elist    


#### program ####

events_list = get_events_list()
#print(events_list)
#events_list = []
#events_list += [{'ID':1, 'Name':'Newbury parkrun #430', 'WebID':'346284', 'PBable':'YES', 'Date':' '}]
#events_list += [{'ID':2, 'Name':'Bramley 10', 'WebID':'277463', 'PBable':'YES', 'Date':' '}]
nEvents = len(events_list)

events_results_dict = get_event_results(events_list)
#print(type(events_results_dict))

#aths* are dictionaries of athletes and points from PBs and races - name:[nPBs,pts1,pts2,...,ptsN], nPBs maxval is 3
aths = {}
aths['Senior Women'] = get_athletes(nEvents,events_results_dict,'W','SEN')
aths['Veteran Women'] = get_athletes(nEvents,events_results_dict,'W','VET')
aths['Senior Men'] = get_athletes(nEvents,events_results_dict,'M','SEN')
aths['Veteran Men'] = get_athletes(nEvents,events_results_dict,'M','VET')

#for group in aths.keys():
#    print(group,aths[group])

for event in events_results_dict:
    for group in aths.keys():
        events_results_dict[event] = get_event_points_by_group(aths[group],events_results_dict.get(event))


#print_events_dict(events_results_dict)

for event in events_list:
    for group in aths.keys():
        aths[group] = assign_athlete_points_by_event(event.get('ID'),aths[group],events_results_dict[event.get('Name')])

for event in events_list:
    for group in aths.keys():
        aths[group] = update_athlete_totals(nEvents,aths[group])

#for group in aths.keys():
#    print(group,aths[group])

pdf = fpdf.FPDF(format='letter') #pdf format
pdf.add_page('L') #create new page
pdf.set_font("Courier", size=10) # font and textsize

print('Events:')
pdf.cell(0, 4.5, txt="Events:", ln=1, align="L")

for event in events_list:
    if event.get('ID')<10:
        print(' {}: {}'.format(event.get('ID'),event.get('Name')))
        pdf.cell(0, 4.5, txt=' {}: {}\n'.format(event.get('ID'),event.get('Name')), ln=1, align="L")
    else:
        print('{}: {}'.format(event.get('ID'),event.get('Name')))
        pdf.cell(0, 4.5, txt='{}: {}\n'.format(event.get('ID'),event.get('Name')), ln=1, align="L")

print('\n')
pdf.cell(0, 5, txt=" ", ln=1, align="L")

max_name_len = 0
for group_name,athlete_group in aths.items():
    max_name_len = max(max_name_len,get_max_name_len(group_name,athlete_group,nEvents))

for group_name,athlete_group in sorted(aths.items(),reverse=True):
    write_results_table(max_name_len,group_name,athlete_group,nEvents,pdf)

pdf.output("league.pdf")







