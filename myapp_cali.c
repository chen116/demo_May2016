// File: deadlineDetectFile.c

// This benchmark is based on the base_task provided in the RT-Xen mailing 
// list and liblitmus.  We make use of the liblitmus libraries to pull the
// consumed and remaining budget. Consumed budget is equal to the execution 
// time.  

// The deadline is detected by checking the time at the end of the job
// execution and comparing to the deadline from the liblitmus syscall.






#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <complex.h>
#include <unistd.h>
#include <sys/time.h>
#include <time.h>

#include "litmus.h"

#define NS_PER_MS         1e6
#define NS_PER_US         1e3

// rmb this has to be 2^n
#define fft_size_or_kalman_iter 1024l

// #define DEBUG

/* Catch errors.
 */
#define CALL( exp ) do { \
int ret; \
ret = exp; \
if (ret != 0) \
fprintf(stderr, "%s failed: %m\n", #exp);\
else \
fprintf(stderr, "%s ok.\n", #exp); \
} while (0)

/* Declare the periodically invoked job.
 * Returns 1 -> task should exit.
 *         0 -> task should continue.
 */
int job(void);

double wcet_f;
double period_f;
int mode;
char filePath[60] = "/dev/shm/vmMon/";
char myPID[20];
char myName[40];
FILE *fp;
int missedJobs = 0;

long long wcet_us;
long dur;
long count;
long size_iter;
typedef double complex cplx;



// These hold the values read from LITMUS-RT
lt_t currentBudget, remainingBudget;
// This is a pointer to the thread control page
struct control_page* pCtrlPage;
struct timespec startTime;
struct timespec stopTime;


double frand() { 
    return 2*((rand()/(double)RAND_MAX) - 0.5); 
} 

int main(int argc, char** argv)
{
    int do_exit, ret;
    struct rt_task param;

    sprintf(myPID,"%d",getpid());
    strcat(filePath,myPID);	
    //argv  1. wcet(ms) 2. period(ms) 3. duration(s) 4. mode (1 for cali sar, 4 for cali kalman) 5. appName 6. size/iter
    
    wcet_f = atoi(argv[1]);    // in ms
    period_f = atof(argv[2]);  // in ms
    size_iter = atof(argv[6]);
    
    wcet_us = (int)(wcet_f*1000);	// Convert ms to us
    
    // wcet_frac = modf(wcet_f,&int_temp);
    // wcet_int = (int)(int_temp);
    
    dur = 1000 * atoi(argv[3]);     // in seconds -> to ms
    mode = atoi(argv[4]);
    count = (dur / period_f);
    
    // printf("wcet_f: %f\tperiod_f: %f\twcet_us: %ld\tcount: %d\n",
    // wcet_f,period_f,wcet_us,count);

    if(argc > 6)
    {
        strncpy(myName,argv[5],40);
    }
    else
    {
        strncpy(myName,"NoNameSet",40);
    }
    printf("Name set: %s\n",myName);
    
    /* Setup task parameters */
    memset(&param, 0, sizeof(param));
    // param.exec_cost = wcet_f * NS_PER_MS;
    // param.period = period_f * NS_PER_MS;
    param.exec_cost = wcet_f * NS_PER_MS;
    param.period = period_f * NS_PER_MS;
    // printf("param.exec: %ld\tparam.period: %ld\n",param.exec_cost, param.period);
    // return 0;
    param.relative_deadline = period_f * NS_PER_MS;
    
    /* What to do in the case of budget overruns? */
    param.budget_policy = NO_ENFORCEMENT;
    
    /* The task class parameter is ignored by most plugins. */
    param.cls = RT_CLASS_SOFT;
    param.cls = RT_CLASS_HARD;
    
    /* The priority parameter is only used by fixed-priority plugins. */
    param.priority = LITMUS_LOWEST_PRIORITY;
    
    /* The task is in background mode upon startup. */
    
    
    /*****
     * 1) Command line paramter parsing would be done here.
     */
    
    
    
    /*****
     * 2) Work environment (e.g., global data structures, file data, etc.) would
     *    be setup here.
     */
    
    
    
    /*****
     * 3) Setup real-time parameters.
     *    In this example, we create a sporadic task that does not specify a
     *    target partition (and thus is intended to run under global scheduling).
     *    If this were to execute under a partitioned scheduler, it would be assigned
     *    to the first partition (since partitioning is performed offline).
     */
    CALL( init_litmus() );
    
    /* To specify a partition, do
     *
     * param.cpu = CPU;
     * be_migrate_to(CPU);
     *
     * where CPU ranges from 0 to "Number of CPUs" - 1 before calling
     * set_rt_task_param().
     */
    CALL( set_rt_task_param(gettid(), &param) );
    
    
    /*****
     * 4) Transition to real-time mode.
     */
    CALL( task_mode(LITMUS_RT_TASK) );
    
    /* The task is now executing as a real-time task if the call didn't fail.
     */
    
    pCtrlPage = get_ctrl_page();

    ret = wait_for_ts_release();
    if (ret != 0)
        printf("ERROR: wait_for_ts_release()");
    
    
    /*****
     * 5) Invoke real-time jobs.
     */
    do {
        /* Wait until the next job is released. */
        sleep_next_period();
        /* Invoke job. */
        do_exit = job();
    } while (!do_exit);
    
    
    
    /*****
     * 6) Transition to background mode.
     */
    CALL( task_mode(BACKGROUND_TASK) );
    
    
    
    /*****
     * 7) Clean up, maybe print results and stats, and exit.
     */
    return 0;
}
void show(const char * s, cplx buf[]) {
        int i;
	printf("%s", s);
        
	for (i=0; i < 8; i++)
		if (!cimag(buf[i]))
			printf("%g ", creal(buf[i]));
		else
			printf("(%g, %g) ", creal(buf[i]), cimag(buf[i]));
}

void _fft(cplx buf[], cplx out[], int n, int step)
{
	int i;
	if (step < n) {
		_fft(out, buf, n, step * 2);
		_fft(out + step, buf + step, n, step * 2);
 
		for (i = 0; i < n; i += 2 * step) {
			cplx t = cexp(-I * 3.1415926 * i / n) * out[i + step];
			buf[i / 2]     = out[i] + t;
			buf[(i + n)/2] = out[i] - t;
		}
	}
}
 
void fft(cplx buf[], int n)
{
        int i;
	cplx out[n];
	for (i = 0; i < n; i++) out[i] = buf[i];
 
	_fft(buf, out, n, 1);
}


void kalman(int iter)
{
//initial values for the kalman filter 
    float x_est_last = 0;
    float P_last = 0; 
    //the noise in the system 
    float Q = 0.022;
    float R = 0.617;
     
    float K; 
    float P; 
    float P_temp; 
    float x_temp_est=0; 
    float x_est=0; 
    float z_measured=0; //the 'noisy' value we measured
    float z_real = 0.5; //the ideal value we wish to measure
    float sum_error_kalman = 0;
    float sum_error_measure = 0;
    int i;     
    srand(0); 
     
    //initialize with a measurement 
    x_est_last = z_real + frand()*0.09;
     
     
    for (i=0;i<iter;i++) {
        //do a prediction 
        x_temp_est = x_est_last; 
        P_temp = P_last + Q; 
        //calculate the Kalman gain 
        K = P_temp * (1.0/(P_temp + R));
        //measure 
        z_measured = z_real + frand()*0.05; //the real measurement plus noise
        //correct 
        x_est = x_temp_est + K * (z_measured - x_temp_est);  
        P = (1- K) * P_temp; 
        //we have our new system 
         
        // printf("Ideal    position: %6.3f \n",z_real); 
        // printf("Mesaured position: %6.3f [diff:%.3f]\n",z_measured,fabs(z_real-z_measured)); 
        // printf("Kalman   position: %6.3f [diff:%.3f]\n",x_est,fabs(z_real - x_est)); 
         
        sum_error_kalman += fabs(z_real - x_est); 
        sum_error_measure += fabs(z_real-z_measured); 
         
        //update our last's 
        P_last = P; 
        x_est_last = x_est; 
}
        // printf ("myName: %s\n",myName);
        // printf("Ideal    position: %6.3f \n",z_real); 
        // printf("Mesaured position: %6.3f [diff:%.3f]\n",z_measured,fabs(z_real-z_measured)); 
        // printf("Kalman   position: %6.3f [diff:%.3f]\n",x_est,fabs(z_real - x_est)); 
return;


}

int job(void)
{
    // long long i = 0;
    // long j = 0;
    long k=0;
    int err;
    lt_t endTime;
    //lt_t beginTime;
    // int bBudgetFlag;

    // Get the start time 
    err = clock_gettime(CLOCK_MONOTONIC, &startTime);
    //beginTime = (unsigned long long)(1E9 * startTime.tv_sec + startTime.tv_nsec);
    if (err != 0)
        perror("clock_gettime");
    
    /* Do real-time calculation. */
	if(mode==1)
	{

		cplx buf[size_iter];
	    for(k=0;k<size_iter;++k)
		{
			if( k < size_iter/2)
				buf[k]=1;
			else
				buf[k]=0;

		}

		fft(buf,size_iter);
	}
	else if (mode==2)
	{
		cplx buf[] = {1, 1, 1, 1, 0, 0, 0, 0};
		fft(buf,8);
	}
	else if(mode==3)
	{
		cplx buf[] = {1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0};
		fft(buf,16);
	}
	else if(mode==4)
	{
		kalman(size_iter);
	}
	else if(mode==5)
	{
		kalman(40);
	}
	else if(mode==6)
	{
		kalman(50);
	}
    
    --count;

    // Check for missed deadlines
    // currentBudget is how long the task has executed for
    // remainingBudget is how much of the allocated budget has been consumed
    get_current_budget(&currentBudget,&remainingBudget);

    // Get the end time
    err = clock_gettime(CLOCK_MONOTONIC, &stopTime);
    if (err != 0)
        perror("clock_gettime");
    endTime = (unsigned long long)(1E9 * stopTime.tv_sec + stopTime.tv_nsec);

    // printf("\tstart:%llu\tend:%llu\tduration:%llu\tdeadline: %llu\n",
    //     (unsigned long long)(1E9 * startTime.tv_sec + startTime.tv_nsec),
    //     endTime,
    //     currentBudget,
    //     pCtrlPage->deadline);

    // if(remainingBudget==0)
    if(endTime > pCtrlPage->deadline)
    {
        // Right now, we just write back the fact that a deadline was missed 
        fp=fopen(filePath, "w+");
        missedJobs++;
        if(fp != NULL)
        {
            // TotalJobsMissed Duration EndTime Deadline
            // Job parameters are most recent missed task
            // fprintf(fp,"%s %d %llu %llu %llu\n", 
            //     myName,
            //     missedJobs, 
            //     endTime, 
            //     currentBudget, 
            //     pCtrlPage->deadline);
            // fclose(fp);
            fprintf(fp,"{\n\t\"DeadlinesMissed\": %d\n}\n", 

                missedJobs);
            fclose(fp);
        }
        else
            printf("\t\tError with file\n");
    }
    // else
    // {
    // 	    double diff_ms = (double)(endTime-beginTime)/1000000.0;
    //         printf("appname:%s missed_jobs:%d beginTime(ns):%llu endTime(ns):%llu exectime(ms):%f deadline(ns):%llu\n", 
    //             myName,
    //             missedJobs, 
    //             beginTime, 
    //             endTime, 
    //             diff_ms,
    //             pCtrlPage->deadline);
    // }
    
    if (count > 0) return 0;   // don't exit
    else return 1;             // exit
}