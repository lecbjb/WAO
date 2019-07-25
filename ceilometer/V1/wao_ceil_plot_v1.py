def data_means_v1(data_out, data_plt, np):
    from time import mktime, strptime
    
    DT = data_out.DT
    
    dur, gates = data_out.BB.shape
    s = ((24*12), gates)
    data_plt.ZZ = np.ones(s)
    data_plt.BB = np.ones(s)
    flagBB = np.ones(s)
    
    s1= ((24*12),6)
    data_plt.DT = np.ones(s1)
    
    s2= (24*12)
    data_plt.DoY = np.ones(s2)
    
    s3= (24*12,3)
    data_plt.CBH = np.ones(s3)
    
    
    count = -1
    for hr in range(0, 24, 1):
        for mn in range(0, 60, 5):
            count = count + 1
            
            data_plt.DT[count,0] = int(DT[0,0])
            data_plt.DT[count,1] = int(DT[0,1])
            data_plt.DT[count,2] = int(DT[0,2])
            data_plt.DT[count,3] = int(hr)
            data_plt.DT[count,4] = int(mn)
            data_plt.DT[count,5] = 0
            
            msg = str(int(DT[0,2])) + '/' + str(int(DT[0,1])) + '/' + str(int(DT[0,0])) + ' '
            msg = msg + str(hr) + ':' + str(mn)
            tt = strptime(msg, '%d/%m/%Y %H:%M')  
            data_plt.DoY[count] = float(tt[7]) + ((((float(tt[5])/60) + float(tt[4]))/60) + float(tt[3]))/24
            
            bb = data_out.BB[((DT[:,3] == hr) & ((DT[:,4] >= mn) & (DT[:,4] < mn + 5))),:]
            cbh = data_out.CBH[((DT[:,3] == hr) & ((DT[:,4] >= mn) & (DT[:,4] < mn + 5))),:]
            zz = data_out.ZZ[((DT[:,3] == hr) & ((DT[:,4] >= mn) & (DT[:,4] < mn + 5))),:]
            
            dur, gates = bb.shape
            if dur > 0:
                data_plt.CBH[count,:] = cbh[0,:]
                if dur == 1:
                    data_plt.ZZ[count,:] = zz
                    data_plt.BB[count,:] = bb
                    data_plt.CBH[count,:] = cbh
                    
                else:
                    for n in range(gates):
                        data_plt.ZZ[count,n] = np.nanmean(zz[:,n])
                        data_plt.BB[count,n] = np.nanmean(bb[:,n])
                        
                    data_plt.CBH[count,0] = np.nanmean(cbh[:,0])
                    data_plt.CBH[count,1] = np.nanmean(cbh[:,1])
                    data_plt.CBH[count,2] = np.nanmean(cbh[:,2])
            else:
                data_plt.ZZ[count,:] = np.nan
                data_plt.BB[count,:] = np.nan
                data_plt.CBH[count,0] = np.nan
                data_plt.CBH[count,1] = np.nan
                data_plt.CBH[count,2] = np.nan
    
    #QC data
    dur, gates = data_plt.BB.shape
    
    ii_min = np.where(data_plt.BB <= 1e-7)
    flagBB[ii_min] = 2
    ii_max = np.where(data_plt.BB >= 1)
    flagBB[ii_max] = 2
    
    #filter - gate
    for i in range(gates-1):
        for ii in range(2,dur-3):
            if ((flagBB[ii-2,i]) and (flagBB[ii,i] == 1) and (flagBB[ii+2,i] != 1)):
                flagBB[ii,i] = 2
    
    #filter - time            
    for i in range(dur-1):
        for ii in range(2,gates-3):
            if ((flagBB[i,ii-2]) and (flagBB[i,ii] == 1) and (flagBB[i,ii+2] != 1)):
                flagBB[i,ii] = 2            
                
    #filter - gate
    for i in range(gates-1):            
        for ii in range(1,dur-2):
            if ((flagBB[ii-1,i]) and (flagBB[ii,i] == 1) and (flagBB[ii+1,i] != 1)):
                flagBB[ii,i] = 2
   
    #filter - time
    for i in range(dur-1):
        for ii in range(1,gates-2):
            if ((flagBB[i,ii-1]) and (flagBB[i,ii] == 1) and (flagBB[i,ii+1] != 1)):
                flagBB[i,ii] = 2
    
    np.putmask(data_plt.BB, flagBB != 1, np.nan)
    np.putmask(data_plt.CBH, (data_plt.CBH >= 8000), np.nan)
    data_plt.BB = np.ma.masked_invalid(data_plt.BB)
    data_plt.CBH = np.ma.masked_invalid(data_plt.CBH)
    
    return data_plt
    
def data_plot_v1(data_plt, np, do):
    from matplotlib import pyplot as plt
    #pull out data to be plotted for easy plotting
    x = (data_plt.DoY - data_plt.DoY[0]) * 24
    y = data_plt.ZZ[1,:]
    z = np.log10(data_plt.BB.transpose())
    #create balck figure object
    fig = plt.figure()
    #plot backscatter profile
    plt.pcolor(x, y, z, cmap='gist_ncar', vmin = np.log10(1e-7), vmax = np.log10(1))
    #plot cloud bases
    plt.hold(True)
    line, = plt.plot(x,data_plt.CBH[:,0],'ko', label='Cloud Base 1')
    line, = plt.plot(x,data_plt.CBH[:,1],'ks', label='Cloud Base 2')
    line, = plt.plot(x,data_plt.CBH[:,2],'k*', label='Cloud Base 3')
    plt.hold(False)
    #get data strings
    yyyy = str(int(data_plt.DT[0,0]))
    mmmm = str(int(data_plt.DT[0,1]))
    if (len(mmmm) < 2):
        mmmm = '0' + mmmm
    dddd = str(int(data_plt.DT[0,2]))
    if (len(dddd) < 2):
        dddd = '0' + dddd
    #put on grid and labels
    plt.grid()
    plt.xlabel('Hour (UTC)')
    plt.ylabel('Height above instrument (m)')
    plt.title('WAO Ceilometer: ' + dddd + '/' + mmmm + '/' + yyyy)
    cb = plt.colorbar()  
    cb.set_label(r'${log}_{10}{(Attenuated Aerosol Backscatter Coefficient)}(m^{-1} sr^{-1})$')    
    plt.legend()
    #create file name
    fn = do + yyyy + mmmm + dddd + '.png'
    #save file 
    plt.savefig(fn, dpi=1200, facecolor='w', edgecolor='w',
        orientation='portrait', papertype='a4', format='png',
        transparent=False, bbox_inches='tight', pad_inches=0.1,
        frameon=None)