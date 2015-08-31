#include "@PROJECT_NAME@/@PROJECT_NAME@.hpp"

namespace lwr{

@CLASS_NAME@::@CLASS_NAME@(const std::string& name):
damping_(10.0),
RTTLWRAbstract(name)
{
    this->addOperation("setDamping",&@CLASS_NAME@::setDamping,this,RTT::OwnThread);
    this->addProperty("damping",damping_).doc("Damping value");
}

bool @CLASS_NAME@::configureHook()
{
    // Configure kdl chains, connect all ports etc.
    bool configure = RTTLWRAbstract::init();
    
    // Try to get parameters from ROS
    this->getAllComponentRelative();
    
    // This is joint imp ctrl + Kp=Kd=0
    setJointTorqueControlMode();
    
    return configure;
}

void @CLASS_NAME@::setDamping(const double damping)
{
    if(damping)
        damping_ = damping;
}

void @CLASS_NAME@::updateHook()
{
    // Get the latest state
    if(!updateState())
        return;
    // Now jnt_pos, jnt_vel are filled with new data
    
    // Zero Grav + Damping
    jnt_trq_cmd = -damping_*jnt_vel;
    
    // Checking if in the right control mode
    if(isCommandMode() && isJointImpedanceControlMode())
        sendJointTorque(jnt_trq_cmd);
}

}
