// @PROJECT_NAME@ - ISIR @YEAR@
// Copyright (c) @AUTHOR@, All rights reserved.
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 3.0 of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License along with this library.

#ifndef __@PROJECT_NAME_UPPER@_HPP__
#define __@PROJECT_NAME_UPPER@_HPP__

#include "rtt_lwr_abstract/rtt_lwr_abstract.hpp"

namespace lwr{
  class @CLASS_NAME@ : public RTTLWRAbstract{
    public:
      @CLASS_NAME@(const std::string& name);
      virtual ~@CLASS_NAME@(){};
      void updateHook();
      bool configureHook();
      void setGain(double gain);
    protected:
      double gain_;
  };
}
ORO_CREATE_COMPONENT(lwr::@CLASS_NAME@)
#endif
