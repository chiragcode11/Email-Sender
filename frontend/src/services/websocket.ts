import { io, Socket } from 'socket.io-client'

class WebSocketService {
    private socket: Socket | null = null
    private url: string = 'http://localhost:8000'

    connect(token: string) {
        if (this.socket?.connected) {
            return
        }

        this.socket = io(this.url, {
            auth: {
                token,
            },
            transports: ['websocket'],
        })

        this.socket.on('connect', () => {
            console.log('WebSocket connected')
        })

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected')
        })

        this.socket.on('error', (error) => {
            console.error('WebSocket error:', error)
        })
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect()
            this.socket = null
        }
    }

    // Subscribe to campaign updates
    subscribeToCampaign(campaignId: number, callback: (data: any) => void) {
        if (!this.socket) {
            console.error('WebSocket not connected')
            return
        }

        this.socket.emit('subscribe_campaign', { campaign_id: campaignId })
        this.socket.on(`campaign_${campaignId}_update`, callback)
    }

    unsubscribeFromCampaign(campaignId: number) {
        if (!this.socket) {
            return
        }

        this.socket.emit('unsubscribe_campaign', { campaign_id: campaignId })
        this.socket.off(`campaign_${campaignId}_update`)
    }

    // Subscribe to email events
    subscribeToEmailEvents(callback: (data: any) => void) {
        if (!this.socket) {
            console.error('WebSocket not connected')
            return
        }

        this.socket.on('email_event', callback)
    }

    unsubscribeFromEmailEvents() {
        if (!this.socket) {
            return
        }

        this.socket.off('email_event')
    }

    isConnected(): boolean {
        return this.socket?.connected || false
    }
}

export const websocketService = new WebSocketService()
