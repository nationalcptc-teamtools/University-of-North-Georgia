#!/usr/bin/env ruby
# frozen_string_literal: true

# A very simple an extensible Ruby socket listener for
# scripting

require 'socket'

BLOCK_SIZE = 1024

# Higher-level version of TCPSocket that can receive
# messages until the host is done sending
class Netcat < TCPSocket
  def initialize(host, port, recv_timeout)
    super(host, port)

    @recv_timeout = recv_timeout
  end

  def receiving?
    IO.select([self], nil, nil, @recv_timeout)
  end

  def receive
    blocks = []
    blocks << recv(BLOCK_SIZE) while receiving?
    blocks
  end
end
