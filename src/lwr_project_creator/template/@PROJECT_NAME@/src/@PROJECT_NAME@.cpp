#include "@PROJECT_NAME@/@PROJECT_NAME@.hpp"

namespace lwr{

@CLASS_NAME@::@CLASS_NAME@(const std::string& name):RTTLWRAbstract(name)
{
    this->addOperation("setGain",&@CLASS_NAME@::setGain,this,RTT::OwnThread);
}

bool @CLASS_NAME@::configureHook()
{
    bool configure = RTTLWRAbstract::configureHook();
    setJointImpedanceControlMode();
    return configure;
}

void @CLASS_NAME@::setGain(double gain)
{
    gain_ = gain;
}

void @CLASS_NAME@::updateHook()
{
    //this->trigger();
}

}
