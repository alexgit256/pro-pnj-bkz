mkdir "lwe-instance-test-new-cost-modelv2"
cd "lwe-instance-test-new-cost-modelv2"
mkdir "default_g6k_main(32+2gpus)"
mkdir "d4f-default-g6k"
cd "d4f-default-g6k"
mkdir "bssa(32+2gpus)"
mkdir "enumbs(32+2gpus)"
cd ..
cd ..

for j in $(seq 1 5) #do
do

    for i in $(seq 55 61) #do
    do
    
    python lwe_instance.py $i --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True  | tee "lwe-instance-test"/"lwe-instance-test-new-cost-modelv2"/"default_g6k_main(32+2gpus)"/$i-010-${j}.log

    # # ###########################################
    # # # EnumBS strategy test:  d4f-default-g6k
    # # #
    # # ###########################################

    python ProPnjBKZ_for_lwe.py ${i} --lwe/alpha 0.010 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_instance" --float_type "dd"| tee "lwe-instance-test"/"lwe-instance-test-new-cost-modelv2"/"d4f-default-g6k"/"enumbs(32+2gpus)"/${i}-010-${j}.log
   
    # # # ###########################################
    # # # # BSSA strategy test: d4f-default-g6k
    # # # #
    # # # ###########################################

    python ProPnjBKZ_for_lwe.py ${i} --lwe/alpha 0.010 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "bssav1" --load_lwe "lwe_instance" --float_type "dd"| tee "lwe-instance-test"/"lwe-instance-test-new-cost-modelv2"/"d4f-default-g6k"/"bssa(32+2gpus)"/${i}-010-${j}.log

    done


done


