#include "@PROJECT_NAME@/@PROJECT_NAME@.hpp"

@CLASS_NAME@::@CLASS_NAME@(const std::string& name):
damping_(1.0),
RTTLWRAbstract(name)
{
    this->addOperation("setDamping",&@CLASS_NAME@::setDamping,this,RTT::OwnThread);
    this->addProperty("damping",damping_).doc("Damping value");
}

bool @CLASS_NAME@::configureHook()
{
    // Configure kdl chains
    bool configure = RTTLWRAbstract::init();

    // Map parameters from ROS to OROCOS Properties
    rtt_ros_kdl_tools::getAllPropertiesFromROSParam(this);

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
    getJointPosition(jnt_pos);
    getJointVelocity(jnt_vel);
    // Now jnt_pos, jnt_vel are filled with new data

    // Zero Grav + Damping
    jnt_trq_cmd = -damping_*jnt_vel;

    sendJointTorque(jnt_trq_cmd);
}
