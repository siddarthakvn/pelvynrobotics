# eeUVsim local patches

Apply after cloning [eeUVsim_Gazebo](https://github.com/Centre-for-Biorobotics/eeUVsim_Gazebo):

```bash
cd ~/auv_ws/src/eeUVsim_Gazebo
git apply ../../patches/eeuvsim_gazebo.patch
```

Patches fix:
- Remove unused `control_msgs` dependency (Humble build)
- Python import paths for `finDynamics` scripts
