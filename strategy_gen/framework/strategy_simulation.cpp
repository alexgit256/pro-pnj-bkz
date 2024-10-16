// #include <boost/math/distributions/chi_squared.hpp>
#include <iostream>
#include "strategy_simulation.h"

using namespace std;
// using namespace boost;



double sim_strategy(Params params, vector<double> l, vector<tuple<int,int,int>> strategy, double sigma){
    cout<<"cost_model = "<<params.cost_model<<endl;
    int dim = int(l.size());
    BKZJSim* sim = new BKZJSim(params,dim);
    COST* cost = new COST(params);
    double Gcum = -1000., Bcum = -1000., cum_pr = 0., rem_pr = 1., GBKZ = -1000.;
    pair<double,double> G;
    for(int i = 0; i<int(strategy.size()); i++){
        int beta = get<0>(strategy[i]), jump = get<1>(strategy[i]), tours = get<2>(strategy[i]);
        for(int t = 0; t< tours; t++){
            double slope = get_current_slope(l, 0, dim);
            int beta_ = get_beta_(params, beta, jump, dim,slope);
            sim -> simulate(l,l,beta,jump,1);
            slope = get_current_slope(l,0,dim);
            boost::math::chi_squared chisquare(beta_);
            // cout<<beta_<<","<<beta<<endl;
            double pr = boost::math::cdf(chisquare,pow(2,2.*l[dim-beta_]));
            // FP_NR<FT> pr = boost::math::cdf(chisquare,pow(2,2.*l[dim-beta_]));
            
            G = cost->bkz_cost(dim,beta,jump,params.cost_model);
            // cout<<"G.first"<<endl;
            if(params.verbose)
                printf("Strategy (%d,%d,%d), slope = %lf, sim-cost = %3.7f log2(sec) = %3.7f sec \n", beta,jump,t+1,slope, G.first ,pow(2,G.first));
            
            GBKZ = log2(pow(2,GBKZ)+pow(2,G.first));
            // cout<<"GBKZ = "<<GBKZ<<", beta = "<<beta<<endl;
            if(not params.worst_case){
                Gcum = log2(pow(2,Gcum)+pow(2,GBKZ)*rem_pr*pr);
                Bcum = log2(pow(2,Bcum)+pow(2,G.second)*rem_pr*pr);
            }
            else{
                Gcum = GBKZ;
                Bcum = max(Bcum, G.second);
            }

            cum_pr += rem_pr * pr;
            rem_pr = 1. - cum_pr;

            // cout<<"cum_pr = "<<cum_pr<<endl;
        } 
    }

    // print_vector(l,0,dim);
    for(int i = 0; i < dim; i++){
        l[i] -= log2(sigma);
    }


    tuple<int,int,double,double,double> dsvp_t_;
    if(params.worst_case)
        dsvp_t_ = dsvp_predict(l, 0., cost, params.cost_model, make_pair(Gcum, Bcum));
    else
        dsvp_t_ = dsvp_predict(l, cum_pr, cost, params.cost_model, make_pair(GBKZ, G.second));
        // cout<<"cum_pr = "<<cum_pr<<endl;
    int dsvp = get<1>(dsvp_t_);
    // int f = wrapper_default_dim4free_fun(dsvp);
    int f = get_f_for_pump(params,dsvp,l);
    // int f = dims4free(dsvp);
    if(params.cost_model==1)
        printf("pump-{%d,%d,%d}, sim-pump cost = %3.7f sec\n",  dim - dsvp, dsvp, f,  get<2>(dsvp_t_)); 
        
    if(params.cost_model>=2)
        printf("pump-{%d,%d,%d}, sim-pump cost = %3.7f sec\n",  dim - dsvp, dsvp, f,  pow(2,get<4>(dsvp_t_))); 

    if(not params.worst_case)
        Gcum = log2(pow(2,Gcum)+pow(2,get<2>(dsvp_t_)));
    else
        Gcum = log2(pow(2,Gcum)+pow(2,get<4>(dsvp_t_)));
         
    // Gcum = log2(pow(2,Gcum)+pow(2,get<4>(dsvp_t_)));
    
    Bcum = max(Bcum, get<3>(dsvp_t_));
    if(params.cost_model>=2)
        cout<<"Gcum = "<<pow(2,Gcum)<<"sec, Bcum = "<<pow(2,Bcum)<<"bits"<<endl;
    if(params.cost_model==1)
        cout<<"Gcum = "<< Gcum <<"gates, Bcum = "<< Bcum<<"bits"<<endl;
    cout<<"============================="<<endl;

    return Gcum;
}


vector<tuple<int,int,int>> get_strategy(long* strategy, int strategy_size){
    vector<tuple<int,int,int>> strategy_vec;
    strategy_vec.resize(strategy_size);
    for(int i = 0; i < strategy_size; i++){
        strategy_vec[i] = {strategy[3*i], strategy[3*i+1],strategy[3*i+2]};
    }
    return strategy_vec;
}

//Simulate the stratey from original lwe instance 
double test_lwechal_from_actual_l(Params params, long* strategy_arr, int strategy_size, double* l_array,int dim){
    // LWEchal* lwechal = gen_lwechal_instance(n, alpha);
    // int dim = lwechal->dim;
    // FP_NR<FT> dvol = lwechal->dvol;
    // vector<double> l = lwechal->log_rr, l_;
    // double  sigma = lwechal->alpha * lwechal->q;
    // // printf("No sigma normalization,");
    // // sim_strategy(params, l, strategy,sigma);

    // printf("After a sigma normalization,");
    // for(int i = 0; i < dim; i++){
    //     l[i] -=  log2(sigma);
    // }
    vector<tuple<int,int,int>> strategy = get_strategy(strategy_arr, strategy_size);
    vector<double> l;
    l.resize(dim);
    for(int i = 0; i < dim; i++){
        l[i] = l_array[i];
    }
    double slope = get_current_slope(l,0,dim);
    printf("slope = %f\n", slope);

    return sim_strategy(params, l, strategy,1.);
}





//Simulate the stratey from gsa-gs-lengths and original lwe instance 
double test_lwechal_from_gsa(Params params, int dim, double dvol, long* strategy_arr, int strategy_size){
    vector<tuple<int,int,int>> strategy = get_strategy(strategy_arr, strategy_size);
    printf("Generate gs-lengths by GSA assumption...\n");
    vector<double>  l = gen_simulated_gso(dim, dvol);
    double slope = get_current_slope(l,0,dim);
    cout<<"Slope of gs-lengths generated by GSA assumption: "<<slope<<endl;

    return sim_strategy(params, l, strategy, 1.);
}


// void test_nist_from_gsa(Params params,int n, int m, int q,  map<int,double> D_e, map<int,double> D_s, vector<tuple<int,int,int>> strategy){
//     printf("Generate gs-lengths by GSA assumption...\n");
//     LWEchal* lwechal = gen_LWE_instance_with_input_distribution( n, q, m, D_e, D_s, params.verbose);
//     vector<double>  l = gen_simulated_gso(lwechal->dim, lwechal->dvol);
//     double slope = get_current_slope(l,0,lwechal->dim);
//     cout<<"Slope of gs-lengths generated by GSA assumption: "<<slope<<endl;

//     sim_strategy(params, l, strategy, 1.);
// }


// int main(){

//     vector<tuple<int,int,int>> strategy;
//     // int n;
//     // double alpha;
//     // Params params = new Params;
//     // params.cost_model = 2;
//     // params.practical_pnjbkz_d4f = 3;
//     // params.practical_pump_d4f = 2;
//     // params.worst_case = true;
//     // params.verbose = true;

//     // vector<tuple<int,int,int>> strategy = {{83, 8, 1}, {93, 8, 1}, {108, 8, 1}, {117, 8, 1}, {119, 4, 1}, {133, 4, 1}};
//     // test_lwechal_from_original_instance(params, n, alpha, strategy);


//     // map<int,double> D_e, D_s;
//     // int n, m , q, eta;
//     // double alpha;
//     // Params params = new Params;
//     // params.cost_model = 2;
//     // params.practical_pnjbkz_d4f = 3;
//     // params.practical_pump_d4f = 3;
//     // params.worst_case = true;
//     // params.verbose = true;
//     // vector<tuple<int,int,int>> strategy;


//     // n = 40, alpha = 0.030;
//     // strategy = {{73,8,1},{89,9,1},{117,10,1},{119,10,1}};
//     // test_lwechal_from_original_instance(params, n, alpha, strategy);



//     params.worst_case = false;
//     params.cost_model = 1;
//     params.theo_pnjbkz_d4f = 2;
//     params.theo_pump_d4f = 2;
//     params.list_decoding = "agps20"; //"matzov22";
//     printf("============= Kyber-1024\n");
//     n = 1024, m = 1024, q = 3329;
//     D_s = build_centered_binomial_law(2);
//     D_e = D_s;
//     // strategy = {};
//     // for(int i = 50; i<= 903; i++){
//     //     strategy.insert(strategy.end(),{i,1,1});
//     // }
//     // test_nist_from_gsa(params, n, m, q, D_e, D_s,strategy);


//     strategy = {{50,7,1},{51,7,1},{52,7,1},{53,7,1},{78,1,1},{79,7,1},{79,4,1},{80,7,1},{80,4,1},{81,7,1},{82,7,1},{82,4,1},{83,7,1},{83,4,1},{84,7,1},{84,4,1},{85,7,1},{85,4,1},{86,7,1},{86,4,1},{87,7,1},{87,4,1},{88,7,1},{88,4,1},{89,7,1},{89,4,1},{90,7,1},{90,4,1},{91,7,1},{91,4,1},{92,7,1},{92,4,1},{93,7,1},{93,4,1},{94,7,1},{94,4,1},{95,7,1},{95,4,1},{96,7,1},{97,7,1},{97,4,1},{98,7,1},{98,4,1},{99,7,1},{99,4,1},{100,7,1},{100,4,1},{101,7,1},{101,4,1},{102,7,1},{102,4,1},{103,7,1},{103,4,1},{104,7,1},{104,4,1},{105,7,1},{105,4,1},{106,7,1},{106,4,1},{107,7,1},{107,4,1},{108,7,1},{108,4,1},{109,7,1},{109,4,1},{110,7,1},{111,7,1},{111,4,1},{112,7,1},{112,4,1},{113,7,1},{113,4,1},{114,7,1},{114,4,1},{115,7,1},{115,4,1},{116,7,1},{116,4,1},{117,7,1},{117,4,1},{118,7,1},{118,4,1},{119,7,1},{119,4,1},{120,7,1},{120,4,1},{121,7,1},{121,4,1},{122,7,1},{122,4,1},{123,7,1},{123,4,1},{124,7,1},{125,7,1},{125,4,1},{126,7,1},{126,4,1},{127,7,1},{127,4,1},{128,7,1},{128,4,1},{129,7,1},{129,4,1},{130,7,1},{130,4,1},{131,7,1},{131,4,1},{132,7,1},{132,4,1},{133,7,1},{133,4,1},{134,7,1},{134,4,1},{135,7,1},{135,4,1},{136,7,1},{136,4,1},{138,10,1},{138,7,1},{138,4,1},{139,10,1},{139,7,1},{140,10,1},{140,4,1},{141,10,1},{142,10,1},{142,4,1},{143,10,1},{144,10,1},{144,4,1},{145,10,1},{146,10,1},{146,4,1},{147,10,1},{148,10,1},{148,7,1},{148,4,1},{149,10,1},{149,7,1},{149,4,1},{150,10,1},{150,7,1},{150,4,1},{151,10,1},{151,7,1},{152,7,1},{152,4,1},{153,10,1},{153,7,1},{153,4,1},{154,10,1},{154,7,1},{154,4,1},{155,10,1},{155,7,1},{155,4,1},{156,10,1},{156,7,1},{156,4,1},{157,10,1},{157,7,1},{157,4,1},{158,10,1},{158,7,1},{158,4,1},{159,10,1},{159,7,1},{159,4,1},{160,10,1},{160,7,1},{160,4,1},{161,10,1},{161,7,1},{161,4,1},{162,10,1},{162,7,1},{162,4,1},{164,10,1},{164,7,1},{165,10,1},{166,10,1},{167,10,1},{168,10,1},{169,10,1},{170,10,1},{171,10,1},{172,10,1},{173,10,1},{173,7,1},{173,4,1},{174,10,1},{175,10,1},{175,7,1},{176,10,1},{177,10,1},{178,10,1},{179,10,1},{180,10,1},{181,10,1},{182,10,1},{182,7,1},{183,10,1},{184,10,1},{185,10,1},{186,10,1},{186,7,1},{187,10,1},{188,10,1},{189,10,1},{190,10,1},{191,10,1},{191,7,1},{193,10,1},{194,10,1},{195,10,1},{196,10,1},{197,10,1},{198,10,1},{198,7,1},{199,10,1},{199,7,1},{201,10,1},{203,10,1},{204,10,1},{205,10,1},{206,10,1},{207,10,1},{208,10,1},{209,10,1},{210,10,1},{210,7,1},{210,4,1},{211,4,1},{212,4,1},{214,4,1},{215,4,1},{216,4,1},{217,4,1},{218,4,1},{219,4,1},{220,4,1},{221,4,1},{222,4,1},{224,4,1},{225,4,1},{226,4,1},{227,4,1},{228,4,1},{229,4,1},{230,4,1},{231,4,1},{232,4,1},{233,4,1},{235,4,1},{236,4,1},{239,4,1},{240,4,1},{241,4,1},{242,4,1},{243,4,1},{245,4,1},{246,4,1},{248,4,1},{250,4,1},{251,4,1},{253,4,1},{254,4,1},{256,4,1},{257,4,1},{259,4,1},{261,4,1},{262,4,1},{264,4,1},{266,4,1},{268,4,1},{269,4,1},{271,4,1},{273,4,1},{275,4,1},{277,4,1},{279,4,1},{280,4,1},{284,4,1},{285,4,1},{286,4,1},{288,4,1},{291,4,1},{292,4,1},{294,4,1},{296,4,1},{299,4,1},{301,4,1},{303,4,1},{305,4,1},{307,4,1},{309,4,1},{312,4,1},{314,4,1},{316,4,1},{319,4,1},{321,4,1},{324,4,1},{326,4,1},{328,4,1},{331,4,1},{334,4,1},{336,4,1},{339,4,1},{342,4,1},{345,4,1},{347,4,1},{350,4,1},{353,4,1},{355,4,1},{359,4,1},{362,4,1},{365,4,1},{368,4,1},{371,4,1},{374,4,1},{377,4,1},{380,4,1},{383,4,1},{387,4,1},{390,4,1},{394,4,1},{397,4,1},{400,4,1},{404,4,1},{407,4,1},{411,4,1},{415,4,1},{419,4,1},{422,4,1},{427,4,1},{430,4,1},{434,4,1},{439,4,1},{443,4,1},{447,4,1},{451,4,1},{455,4,1},{460,4,1},{465,4,1},{469,4,1},{474,4,1},{479,4,1},{483,4,1},{489,4,1},{493,4,1},{499,4,1},{504,4,1},{509,4,1},{514,4,1},{520,4,1},{526,4,1},{532,4,1},{538,4,1},{543,4,1},{549,4,1},{555,4,1},{562,4,1},{568,4,1},{575,4,1},{581,4,1},{589,4,1},{595,4,1},{603,4,1},{610,4,1},{617,4,1},{626,4,1},{634,4,1},{641,4,1},{649,4,1},{658,4,1},{666,4,1},{676,4,1},{685,4,1},{694,4,1},{703,4,1},{714,4,1},{723,4,1},{734,4,1},{745,4,1},{755,4,1},{766,4,1},{778,4,1},{789,4,1},{801,4,1},{814,4,1},{826,4,1}};
//     test_nist_from_gsa(params, n, m, q, D_e, D_s,strategy);


    
// }