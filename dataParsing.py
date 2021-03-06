import csv
noise=2e9
infotime=1000000 #in micro sec
predicttime=1800*infotime
back_trace=5
t0=1800019613

def basic_price(sym):
    with open('data/data2.csv') as csv_infile:
        with open('data/data'+sym+'.csv', mode='w') as csv_outfile:
            csv_reader=csv.reader(csv_infile, delimiter=',')
            csv_writer=csv.writer(csv_outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            line_count=0
            lasttime=-1
            tottime=0
            totline=0
            for row in csv_reader:
                if line_count>=1:
                    [time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                    if bid!='0' and ask!='0' and symbol=='STOCK'+sym:
                        if lasttime==-1:
                            lasttime=long(time)
                        else:
                            timedif=long(time)-lasttime
                            lasttime=long(time)
                            tottime+=timedif
                            csv_writer.writerow([time,symbol,bid,ask,timedif])
                        totline+=1
                line_count+=1
            print tottime, totline

def basic_price_change(sym):
    with open('data/data2.csv') as csv_infile:
        with open('data/data'+sym+'_pricechange.csv', mode='w') as csv_outfile:
            csv_reader=csv.reader(csv_infile, delimiter=',')
            csv_writer=csv.writer(csv_outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            lasttime=-1
            lastbid=0
            lastask=0
            csv_reader.next();
            for row in csv_reader:
                [time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                if bid!='0' and ask!='0' and symbol=='STOCK'+sym:
                    if lasttime==-1:
                        lasttime=long(time)
                        lastbid=bid
                        lastask=ask
                    else:
                        if bid!=lastbid or ask!=lastask:
                            lastbid=bid
                            lastask=ask
                            timedif=long(time)-lasttime
                            lasttime=long(time)
                            csv_writer.writerow([time,symbol,bid,ask,timedif])

def basic_trd(sym):
    with open('data/data2.csv') as csv_infile:
        with open('data/data'+sym+'_trd.csv', mode='w') as csv_outfile:
            csv_reader=csv.reader(csv_infile, delimiter=',')
            csv_writer=csv.writer(csv_outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            line_count=0
            lasttime=-1
            tottime=0
            totline=0
            for row in csv_reader:
                if line_count>=1:
                    [time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                    if trdsz!='0' and trdsd!='0' and symbol=='STOCK'+sym:
                        if lasttime==-1:
                            lasttime=long(time)
                        else:
                            timedif=long(time)-lasttime
                            lasttime=long(time)
                            tottime+=timedif
                            #csv_writer.writerow([time,symbol,bid,ask,timedif])
                            #csv_writer.writerow([time,symbol,trdsz,trdsd,trdpx])
                        totline+=1
                line_count+=1
            print tottime, totline

def price_interpolate(sym):#interpolate based infotime steps
    with open('data/data2.csv') as csv_infile:
        with open('data/data'+sym+'_int.csv', mode='w') as csv_outfile:
            csv_reader=csv.reader(csv_infile, delimiter=',')
            csv_writer=csv.writer(csv_outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            line_count=0
            tstep=infotime
            count=int(noise/infotime)#get rid of noise part
            lasttime=-1
            lastask=0
            lastbid=0
            currenttime=0
            for row in csv_reader:
                if line_count>=1:
                    [time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                    if bid!='0' and ask!='0' and symbol==('STOCK'+sym):
                        if long(time)-t0<count*tstep: # this point still earlier
                            lasttime=long(time)
                            lastbid=long(bid)
                            lastask=long(ask)
                        else:
                            currenttime=t0+count*tstep
                            while long(time)>=currenttime:
                                #change time unit to count 
                                csv_writer.writerow([count,symbol,lastbid,lastask,int(bidsz),int(asksz)])
                                count+=1
                                currenttime=t0+count*tstep
                            lasttime=long(time)
                            lastbid=long(bid)
                            lastask=long(ask)
                line_count+=1
                #if line_count>1000000:
                #    break

def training_naive_noduplicate(sym):
    '''
    predictors: long term and short term trend
        t-1: bidprice deltaT1
        t-2: bidprice deltaT2
        t-3: bidprice deltaT3
        t-4: bidprice deltaT4
        t-20: bidprice deltaT20
        t-50: bidprice deltaT50
        t-100: bidprice deltaT100
        t-200: bidprice deltaT200
        t-500: bidprice deltaT500
        t-1000: bidprice deltaT1000

    response:
        t: bidprice
    '''
    with open('data/data2.csv') as csv_infile:
        with open('data/data'+sym+'_pre.csv', mode='w') as csv_outfile_pre:
            with open('data/data'+sym+'_res.csv', mode='w') as csv_outfile_res:
                csv_reader=csv.reader(csv_infile, delimiter=',')
                csv_writer_pre=csv.writer(csv_outfile_pre, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer_res=csv.writer(csv_outfile_res, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                basename='STOCK'+sym
                tm1=[]
                tm2=[]
                csv_reader.next() # get rid fo title line
                line_count=0
                #dump the first 2500 lines (too much fluctuations)
                for i in xrange(2500):
                    csv_reader.next()
                old_data=[]
                #collect the first 1001 entries 
                while len(old_data)<1001:
                    row=csv_reader.next()
                    [time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                    if symbol==basename:
                        if bid!='0' and ask!='0':
                            bidprice=long(bid)
                            askprice=long(ask)
                        else:
                            bidprice=long(trdpx)
                            askprice=long(trdpx)
                        statuslist=[time, bidprice, askprice]
                        if tm1 and tm2:
                            #if different from previous time
                            if statuslist[1]!=tm1[1] or statuslist[2]!=tm1[2]:
                                #if tm1==tm2, tm1 end of same price, need to store
                                if tm2[1]==tm1[1] and tm2[2]==tm1[2]:
                                    old_data.append(tm1)
                                #otherwise tm1 already written in file
                                old_data.append(statuslist)
                        else:
                            old_data.append(statuslist)
                        tm2=list(tm1)
                        tm1=list(statuslist)
                #parsing predictors
                for row in csv_reader:
                    [time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                    if symbol==basename:
                        if bid!='0' and ask!='0':
                            bidprice=long(bid)
                            askprice=long(ask)
                        else:
                            bidprice=long(trdpx)
                            askprice=long(trdpx)
                        statuslist=[time, bidprice, askprice]
                        #if different from previous time
                        if statuslist[1]!=tm1[1] or statuslist[2]!=tm1[2]:
                            #if tm1==tm2, tm1 end of same price, need to store
                            if tm2[1]==tm1[1] and tm2[2]==tm1[2]:
                                csv_writer_pre.writerow([tm1[0]]+old_data[-2]+old_data[-3]+old_data[-4]+old_data[-5]+old_data[-11]+old_data[-21]+old_data[-51]+old_data[-101]+old_data[-201]+old_data[-501]+old_data[-1001])
                                csv_writer_res.writerow([tm1[1]])

                            #otherwise tm1 already written in file
                            old_data=old_data[1:]
                            old_data.append(statuslist)
                            csv_writer_pre.writerow([statuslist[0]]+old_data[-2]+old_data[-3]+old_data[-4]+old_data[-5]+old_data[-11]+old_data[-21]+old_data[-51]+old_data[-101]+old_data[-201]+old_data[-501]+old_data[-1001])
                            csv_writer_res.writerow([statuslist[1]]);
                        tm2=list(tm1)
                        tm1=list(statuslist)
                #parsing predictors

def training_naive(sym):
    '''
    predictors: long term and short term trend
        t-1: bidprice deltaT1
        t-2: bidprice deltaT2
        t-3: bidprice deltaT3
        t-4: bidprice deltaT4
        t-20: bidprice deltaT20
        t-50: bidprice deltaT50
        t-100: bidprice deltaT100
        t-200: bidprice deltaT200
        t-500: bidprice deltaT500
        t-1000: bidprice deltaT1000

    response:
        t: bidprice
    '''
    with open('data/data'+sym+'.csv') as csv_infile:
        with open('data/data'+sym+'_pre.csv', mode='w') as csv_outfile_pre:
            with open('data/data'+sym+'_res.csv', mode='w') as csv_outfile_res:
                csv_reader=csv.reader(csv_infile, delimiter=',')
                csv_writer_pre=csv.writer(csv_outfile_pre, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer_res=csv.writer(csv_outfile_res, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                basename='STOCKB'
                tm1=[]
                tm2=[]
                csv_reader.next() # get rid fo title line
                line_count=0
                #dump the first 2500 lines (too much fluctuations)
                for i in xrange(2500):
                    csv_reader.next()
                old_data=[]
                #collect the first 1001 entries 
                while len(old_data)<1001:
                    row=csv_reader.next()
                    #[time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                    [time, symbol, bid, ask]=row
                    if symbol==basename:
                        if bid!='0' and ask!='0':
                            bidprice=long(bid)
                            askprice=long(ask)
                        else:
                            bidprice=long(trdpx)
                            askprice=long(trdpx)
                        statuslist=[time, bidprice, askprice]
                        old_data.append(statuslist)
                #parsing predictors
                for row in csv_reader:
                    #[time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                    [time, symbol, bid, ask]=row
                    if symbol==basename:
                        if bid!='0' and ask!='0':
                            bidprice=long(bid)
                            askprice=long(ask)
                        else:
                            bidprice=long(trdpx)
                            askprice=long(trdpx)
                        statuslist=[time, bidprice, askprice]
                        csv_writer_pre.writerow([statuslist[0]]+old_data[-2]+old_data[-3]+old_data[-4]+old_data[-5]+old_data[-11]+old_data[-21]+old_data[-51]+old_data[-101]+old_data[-201]+old_data[-501]+old_data[-1001])
                        csv_writer_res.writerow([statuslist[1]]);
                        #update old data
                        old_data=old_data[1:]
                        old_data.append(statuslist)

def training(sym):
    '''
    predictors: long term and short term trend
        t-1: price deltaT1
        t-2: price deltaT2
        t-3: price deltaT3
        t-4: price deltaT4
        t-10: price deltaT10
        t-100: price deltaT100
        t-1000: price deltaT1000
        ... until 10*predicttime

    response:
        t: bidprice
    '''
    with open('data/data'+sym+'.csv') as csv_infile:
        with open('data/data'+sym+'_parsed.csv', mode='w') as csv_outfile:
                csv_reader=csv.reader(csv_infile, delimiter=',')
                csv_writer=csv.writer(csv_outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                basename='STOCK'+sym[0]
                tm1=[]
                tm2=[]
                old_data=[]
                data_length=back_trace*predicttime/infotime
                #collect the first bunch of entries 
                while len(old_data)<data_length:
                    row=csv_reader.next()
                    #[time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                    [time, symbol, bid, ask, bidsz, asksz]=row
                    if symbol==basename:
                        if bid!='0' and ask!='0':
                            bidprice=long(bid)
                            askprice=long(ask)
                        else:
                            bidprice=long(trdpx)
                            askprice=long(trdpx)
                        statuslist=[bidprice, askprice, bidsz, asksz]
                        old_data.append(statuslist)
                #parsing predictors
                for row in csv_reader:
                    #[time, symbol, bid, bidsz, ask, asksz, trdsz, trdsd, trdpx]=row
                    [time, symbol, bid, ask, bidsz, asksz]=row
                    if symbol==basename:
                        if bid!='0' and ask!='0':
                            bidprice=long(bid)
                            askprice=long(ask)
                        else:
                            bidprice=long(trdpx)
                            askprice=long(trdpx)
                        statuslist=[bidprice, askprice, bidsz, asksz]

                        #parse the output list
                        back_length=predicttime/infotime
                        outputlist=[time]+list(statuslist)
                        #small info steps
                        #for i in xrange(1,5):
                        #    outputlist+=old_data[-back_length-i]
                        #large info steps
                        i=64
                        while i<predicttime/infotime:
                            outputlist+=old_data[-back_length-i]
                            i*=2
                        #small predict steps
                        for i in xrange(1,back_trace):
                            outputlist+=old_data[-back_length-i*predicttime/infotime]

                        csv_writer.writerow(outputlist)
                        #update old data
                        old_data=old_data[1:]
                        old_data.append(statuslist)

def output(time, trueresult, predictions):
    with open('data/'+time+'.csv') as csv_infile1:
        with open('data/'+trueresult+'.csv') as csv_infile2:
            with open('data/'+predictions+'.csv') as csv_infile3:
                with open('data/'+predictions+'_combined.csv', mode='w') as csv_outfile:
                    csv_reader1=csv.reader(csv_infile1, delimiter=',')
                    csv_reader2=csv.reader(csv_infile2, delimiter=',')
                    csv_reader3=csv.reader(csv_infile3, delimiter=',')
                    csv_writer=csv.writer(csv_outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    for row in csv_reader1:
                        timevalue=row[0] # get rid fo title line
                        truev=csv_reader2.next()[0] # get rid fo title line
                        prev=csv_reader3.next()[0] # get rid fo title line
                        csv_writer.writerow([timevalue,truev,prev]);

def file_divider(symbol):
    inname='data/data'+symbol+'.csv'
    outname1='data/data'+symbol+'_train.csv'
    outname2='data/data'+symbol+'_test.csv'
    row_count=0
    with open(inname) as csv_infile:
        csv_reader=csv.reader(csv_infile, delimiter=',')
        row_count=sum(1 for row in csv_reader)
    row_count=min(row_count,20000)
    with open(inname) as csv_infile:
        with open(outname1, mode='w') as csv_train:
            with open(outname2, mode='w') as csv_test:
                csv_reader=csv.reader(csv_infile, delimiter=',')
                csv_train_writer=csv.writer(csv_train, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_test_writer=csv.writer(csv_test, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                linelimit=int(0.7*row_count)
                line_count=0
                for row in csv_reader:
                    if line_count<linelimit:
                        csv_train_writer.writerow(row)
                    else:
                        csv_test_writer.writerow(row)
                    line_count+=1

#output('dataA_test_pre','dataA_test_res','dataA_test_result')

price_interpolate('A')
training('A_int')

price_interpolate('B')
training('B_int')
#basic_price_change('A')
