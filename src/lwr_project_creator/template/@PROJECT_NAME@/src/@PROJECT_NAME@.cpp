#include "@PROJECT_NAME@/@PROJECT_NAME@.hpp"

@CLASS_NAME@::@CLASS_NAME@(const std::string& name):
RTT::TaskContext(name)
{
    // Here you can add your ports, properties and operations
    // Meanwhile, GenericArmController initialize the Arm() object, i.e. your model
    // and sets
    // and GenericController add the basic orocos ports
    this->addPort("JointPosition",port_joint_position_in).doc("Current joint positions");
    this->addPort("JointVelocity",port_joint_velocity_in).doc("Current joint velocities");
    this->addPort("JointTorque",port_joint_torque_in).doc("Current joint torques");

    this->addPort("JointPositionCommand",port_joint_position_cmd_out).doc("Command joint positions");
    this->addPort("JointVelocityCommand",port_joint_velocity_cmd_out).doc("Command joint velocities");
    this->addPort("JointTorqueCommand",port_joint_torque_cmd_out).doc("Command joint torques");

}

bool @CLASS_NAME@::configureHook()
{
    if(!this->arm.init())
    {
        RTT::log(RTT::Fatal)
        << "Could not initialize arm, make sure roscore is launched"
        " as well as tip_link, root_link and robot_description"
        << RTT::endlog();
    }

    jnt_pos_in.setZero(arm.getNrOfJoints());
    jnt_vel_in.setZero(arm.getNrOfJoints());
    jnt_trq_in.setZero(arm.getNrOfJoints());

    jnt_pos_cmd_out.setZero(arm.getNrOfJoints());
    jnt_vel_cmd_out.setZero(arm.getNrOfJoints());
    jnt_trq_cmd_out.setZero(arm.getNrOfJoints());

    port_joint_position_cmd_out.setDataSample(jnt_pos_cmd_out);
    port_joint_velocity_cmd_out.setDataSample(jnt_vel_cmd_out);
    port_joint_torque_cmd_out.setDataSample(jnt_trq_cmd_out);

    return true;
}

void @CLASS_NAME@::updateHook()
{
    // Read status from robot
    port_joint_position_in.read(jnt_pos_in);
    port_joint_velocity_in.read(jnt_vel_in);

    // Update Internal model
    this->arm.setState(jnt_pos_in,jnt_vel_in);

}

// Let orocos know how to create the component
ORO_CREATE_COMPONENT(@CLASS_NAME@)
