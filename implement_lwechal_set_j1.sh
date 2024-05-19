cd "lwechal-test"
mkdir "lwechal-test-new-cost-modelv2-set-j1"
cd "lwechal-test-new-cost-modelv2-set-j1"
mkdir "default_g6k_main(32+2gpus)"
mkdir "d4f-default-g6k"
cd "d4f-default-g6k"
mkdir "bssa(32+2gpus)"
mkdir "enumbs(32+2gpus)"
cd ..
cd ..
cd ..

for j in $(seq 1 5) #do
do

    # python lwe_challenge.py 40 --lwe/alpha 0.025 --threads 32 --gpus 2 --verbose True --pump/down_sieve True  | tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"default_g6k_main(32+2gpus)"/40-025-${j}.log

    # python lwe_challenge.py 40 --lwe/alpha 0.030 --threads 32 --gpus 2 --verbose True --pump/down_sieve True  | tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"default_g6k_main(32+2gpus)"/40-030-${j}.log

    # python lwe_challenge.py 45 --lwe/alpha 0.020 --threads 32 --gpus 2 --verbose True --pump/down_sieve True  | tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"default_g6k_main(32+2gpus)"/45-020-${j}.log

    # python lwe_challenge.py 50 --lwe/alpha 0.015 --threads 32 --gpus 2 --verbose True --pump/down_sieve True  | tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"default_g6k_main(32+2gpus)"/50-015-${j}.log

    # # ###########################################
    # # # EnumBS strategy test:  d4f-default-g6k
    # # #
    # # ###########################################

    python ProPnjBKZ_for_lwe.py 40 --lwe/alpha 0.025 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --set_j1 1| tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"d4f-default-g6k"/"enumbs(32+2gpus)"/40-025-${j}.log
   
    python ProPnjBKZ_for_lwe.py 40 --lwe/alpha 0.030 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --set_j1 1| tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"d4f-default-g6k"/"enumbs(32+2gpus)"/40-030-${j}.log

    python ProPnjBKZ_for_lwe.py 45 --lwe/alpha 0.020 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --set_j1 1| tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"d4f-default-g6k"/"enumbs(32+2gpus)"/45-020-${j}.log

    python ProPnjBKZ_for_lwe.py 50 --lwe/alpha 0.015 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --set_j1 1| tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"d4f-default-g6k"/"enumbs(32+2gpus)"/50-015-${j}.log

    # # # ###########################################
    # # # # BSSA strategy test: d4f-default-g6k
    # # # #
    # # # ###########################################


    python ProPnjBKZ_for_lwe.py 40 --lwe/alpha 0.025 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "bssav1" --load_lwe "lwe_challenge" --float_type "dd" --set_j1 1| tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"d4f-default-g6k"/"bssa(32+2gpus)"/40-025-${j}.log
   
    python ProPnjBKZ_for_lwe.py 40 --lwe/alpha 0.030 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "bssav1" --load_lwe "lwe_challenge" --float_type "dd" --set_j1 1| tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"d4f-default-g6k"/"bssa(32+2gpus)"/40-030-${j}.log

    python ProPnjBKZ_for_lwe.py 45 --lwe/alpha 0.020 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "bssav1" --load_lwe "lwe_challenge" --float_type "dd" --set_j1 1| tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"d4f-default-g6k"/"bssa(32+2gpus)"/45-020-${j}.log

    python ProPnjBKZ_for_lwe.py 50 --lwe/alpha 0.015 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "bssav1" --load_lwe "lwe_challenge" --float_type "dd" --set_j1 1| tee "lwechal-test"/"lwechal-test-new-cost-modelv2-set-j1"/"d4f-default-g6k"/"bssa(32+2gpus)"/50-015-${j}.log

done


