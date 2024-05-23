mkdir "mode_comparison(32+2gpus)"
cd "mode_comparison(32+2gpus)"
mkdir "two-step"
mkdir "default-g6k"
mkdir "bkz-only"
cd ..



for i in $(seq 1 5) #do
do
###########################################
# LWE instance solved by default G6K test
#
###########################################


python lwe_instance.py 55 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True | tee "mode_comparison(32+2gpus)"/"default-g6k"/55-010-${i}.log

python lwe_instance.py 59 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True | tee "mode_comparison(32+2gpus)"/"default-g6k"/59-010-${i}.log


python lwe_instance.py 61 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True  | tee "mode_comparison(32+2gpus)"/"default-g6k"/61-010-${i}.log


python lwe_instance.py 67 --lwe/alpha 0.005 --threads 32 --gpus 2 --verbose True --pump/down_sieve True | tee "mode_comparison(32+2gpus)"/"default-g6k"/67-005-${i}.log


# ###########################################
# # two-step mode
# #
# ###########################################


python lwe_two_step.py 55 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True --load_lwe "lwe_instance" | tee "mode_comparison(32+2gpus)"/"two-step"/55-010-${i}.log


python lwe_two_step.py 59 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True  --load_lwe "lwe_instance"  | tee "mode_comparison(32+2gpus)"/"two-step"/59-010-${i}.log

python lwe_two_step.py 61 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True --load_lwe "lwe_instance" | tee "mode_comparison(32+2gpus)"/"two-step"/61-010-${i}.log

python lwe_two_step.py 67 --lwe/alpha 0.005 --threads 32 --gpus 2 --verbose True --pump/down_sieve True --load_lwe "lwe_instance" | tee "mode_comparison(32+2gpus)"/"two-step"/67-005-${i}.log





# ###########################################
# # bkz-only
# #
# ###########################################


python lwe_BKZ_only.py 55 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True --load_lwe "lwe_instance"  | tee "mode_comparison(32+2gpus)"/"bkz-only"/55-010-${i}.log

python lwe_BKZ_only.py 59 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True --load_lwe "lwe_instance"  | tee "mode_comparison(32+2gpus)"/"bkz-only"/59-010-${i}.log

python lwe_BKZ_only.py 61 --lwe/alpha 0.010 --threads 32 --gpus 2 --verbose True --pump/down_sieve True --load_lwe "lwe_instance"  | tee "mode_comparison(32+2gpus)"/"bkz-only"/61-010-${i}.log

python lwe_BKZ_only.py 67 --lwe/alpha 0.005 --threads 32 --gpus 2 --verbose True --pump/down_sieve True --load_lwe "lwe_instance"  | tee "mode_comparison(32+2gpus)"/"bkz-only"/67-005-${i}.log


done 