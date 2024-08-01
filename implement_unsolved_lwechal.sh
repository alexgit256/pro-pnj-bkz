mkdir "strategy-for-unsolved-lwechal"

# # ###########################################
# # # EnumBS strategy test:  d4f-default-g6k
# # #
# # ###########################################
# use ./rebuild.sh, don't turn on noyr

#machine A and machine C: max_RAM = 1.5 TB, set max_RAM = 43 log2(bit) = 1TB 
# python ProPnjBKZ_for_lwe.py 40 --lwe/alpha 0.035 --gpus 2 --threads 60 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --max_RAM 43.58 | tee "strategy-for-unsolved-lwechal"/40-035.log


python ProPnjBKZ_for_lwe.py 40 --lwe/alpha 0.035 --gpus 2 --threads 60 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --max_RAM 43 --gen_strategy_only 1 | tee "strategy-for-unsolved-lwechal"/40-035-gen-pump-limit.log

python ProPnjBKZ_for_lwe.py 40 --lwe/alpha 0.040 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --gen_strategy_only 1 --max_RAM 43.58 | tee "strategy-for-unsolved-lwechal"/40-040-pump-limit.log

python ProPnjBKZ_for_lwe.py 50 --lwe/alpha 0.025 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --gen_strategy_only 1 --max_RAM 43.58 | tee "strategy-for-unsolved-lwechal"/50-025-pump-limit.log

python ProPnjBKZ_for_lwe.py 55 --lwe/alpha 0.020 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --gen_strategy_only 1 --max_RAM 43.58 | tee "strategy-for-unsolved-lwechal"/55-020-pump-limit.log

python ProPnjBKZ_for_lwe.py 65 --lwe/alpha 0.015 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --gen_strategy_only 1 --max_RAM 43.58| tee "strategy-for-unsolved-lwechal"/60-015-pump-limit.log
   
python ProPnjBKZ_for_lwe.py 75 --lwe/alpha 0.010 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --gen_strategy_only 1 --max_RAM 43.58| tee "strategy-for-unsolved-lwechal"/75-010-pump-limit.log


# python ProPnjBKZ_for_lwe.py 80 --lwe/alpha 0.005 --gpus 2 --threads 60 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" | tee "strategy-for-unsolved-lwechal"/80-005-2.log

#machine B: max_RAM = 512 GB, set max_RAM = 42 log2(bit) = 1.5TB 
python ProPnjBKZ_for_lwe.py 90 --lwe/alpha 0.005 --gpus 2 --threads 32 --verbose True --pump/down_sieve True  --strategy_method "enumbs" --load_lwe "lwe_challenge" --float_type "dd" --gen_strategy_only 1 --max_RAM 42 | tee "strategy-for-unsolved-lwechal"/90-005-pump-limit.log


# # #default g6k.
# python lwe_challenge.py 40 --lwe/alpha 0.035 --threads 32 --gpus 2 --verbose True --pump/down_sieve True | tee "strategy-for-unsolved-lwechal/40-035-default-g6k.log"