package api

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"

	maxbot "github.com/max-messenger/max-bot-api-client-go"
	"github.com/max-messenger/max-bot-api-client-go/schemes"
)

// VideoUrls представляет URL-ы для воспроизведения видео в разных разрешениях
type VideoUrls struct {
	Url1080p *string `json:"url_1080p,omitempty"`
	Url720p  *string `json:"url_720p,omitempty"`
	Url480p  *string `json:"url_480p,omitempty"`
	Url360p  *string `json:"url_360p,omitempty"`
	Url240p  *string `json:"url_240p,omitempty"`
	Url144p  *string `json:"url_144p,omitempty"`
}

// VideoAttachmentDetails представляет подробную информацию о видео
type VideoAttachmentDetails struct {
	Token     string                    `json:"token"`
	Urls      *VideoUrls                `json:"urls,omitempty"`
	Thumbnail *schemes.PhotoAttachmentPayload `json:"thumbnail,omitempty"`
	Width     int                       `json:"width"`
	Height    int                       `json:"height"`
	Duration  int                       `json:"duration"`
}

// VideosAPI предоставляет методы для работы с видео
type VideosAPI struct {
	api *maxbot.Api
}

// NewVideosAPI создает новый экземпляр VideosAPI
func NewVideosAPI(api *maxbot.Api) *VideosAPI {
	return &VideosAPI{api: api}
}

// GetVideoDetails возвращает подробную информацию о прикрепленном видео
// GET /videos/{videoToken}
func (v *VideosAPI) GetVideoDetails(ctx context.Context, videoToken string) (*VideoAttachmentDetails, error) {
	client := getClient(v.api)
	if client == nil {
		return nil, fmt.Errorf("client is not available")
	}

	result := new(VideoAttachmentDetails)
	values := url.Values{}
	body, err := client.request(ctx, http.MethodGet, fmt.Sprintf("videos/%s", videoToken), values, false, nil)
	if err != nil {
		return result, err
	}
	defer func() {
		if err := body.Close(); err != nil {
			log.Println(err)
		}
	}()
	return result, json.NewDecoder(body).Decode(result)
}

